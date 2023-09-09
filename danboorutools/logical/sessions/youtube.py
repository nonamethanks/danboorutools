from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

import ring

from danboorutools.exceptions import NotLoggedInError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel

if TYPE_CHECKING:
    from requests import Response

JSON_DATA_PATTERN = re.compile(r"ytInitialData = ({.*?});")


class YoutubeSession(Session):
    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = kwargs.get("cookies", {}) | {"SOCS": "CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg"}
        return super().request(*args, **kwargs)

    @ring.lru()
    def channel_data(self, artist_url: str) -> YoutubeChannelData:
        request = self.get(f"{artist_url}/about")
        json_data = JSON_DATA_PATTERN.search(request.text)
        if not json_data:
            if "Before you continue to YouTube" in request.text:
                raise NotLoggedInError(request)
            raise NotImplementedError(artist_url)
        return YoutubeChannelData(**json.loads(json_data.groups()[0]))


class _YoutubeUserData(BaseModel):
    title: str
    description: str
    vanityChannelUrl: str


class YoutubeChannelData(BaseModel):
    metadata: dict
    contents: dict

    @property
    def user_data(self) -> _YoutubeUserData:
        return _YoutubeUserData(**self.metadata["channelMetadataRenderer"])

    @property
    def channel_title(self) -> str:
        return self.user_data.title

    @property
    def vanity_url(self) -> Url:
        return Url.parse(self.user_data.vanityChannelUrl)

    @property
    def related_urls(self) -> list[Url]:
        urls: list[str] = []

        about_tab, = (
            tab["tabRenderer"]
            for tab in self.contents["twoColumnBrowseResultsRenderer"]["tabs"]
            if tab.get("tabRenderer", {}).get("selected")
        )
        if not about_tab["endpoint"]["commandMetadata"]["webCommandMetadata"]["url"].endswith("/about"):
            raise NotImplementedError(about_tab)

        old_links = []
        new_links = []
        for section_content in about_tab["content"]["sectionListRenderer"]["contents"]:
            for item_section in section_content["itemSectionRenderer"]["contents"]:
                try:
                    link_sections = item_section["channelAboutFullMetadataRenderer"]["primaryLinks"]
                except KeyError:
                    pass
                else:
                    old_links += link_sections

                try:
                    link_sections = item_section["channelAboutFullMetadataRenderer"]["links"]
                except KeyError:
                    pass
                else:
                    new_links += link_sections

        urls += [link["navigationEndpoint"]["urlEndpoint"]["url"] for link in old_links]
        urls += [
            link["channelExternalLinkViewModel"]["link"]["commandRuns"][0]["onTap"]["innertubeCommand"]["commandMetadata"]["webCommandMetadata"]["url"]  # pylint: disable=line-too-long  # noqa: E501
            for link in new_links  # youtube devs you fucking monkeys what the fuck are you doing
        ]

        return [Url.parse(u) for u in list(dict.fromkeys(urls))]
