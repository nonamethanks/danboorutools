from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

import ring

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel

if TYPE_CHECKING:
    from requests import Response

JSON_DATA_PATTERN = re.compile(r"ytInitialData = ({.*?});")


class YoutubeSession(Session):
    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = kwargs.get("cookies", {}) | {"CONSENT": "YES+cb.20211212-16-p1.en+FX+793"}
        return super().request(*args, **kwargs)

    @ring.lru()
    def channel_data(self, artist_url: str) -> YoutubeChannelData:
        request = self.get(f"{artist_url}/about", cached=True)
        json_data = JSON_DATA_PATTERN.search(request.text)
        if not json_data:
            raise NotImplementedError
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

        links = []
        for section_content in about_tab["content"]["sectionListRenderer"]["contents"]:
            for item_section in section_content["itemSectionRenderer"]["contents"]:
                try:
                    link_sections = item_section["channelAboutFullMetadataRenderer"]["primaryLinks"]
                except KeyError:
                    pass
                else:
                    links += link_sections

        urls += [link["navigationEndpoint"]["urlEndpoint"]["url"] for link in links]

        return [Url.parse(u) for u in list(dict.fromkeys(urls))]
