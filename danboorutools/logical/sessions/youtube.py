from __future__ import annotations

import json
import re

import ring

from danboorutools.logical.sessions import ScraperResponse, Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel


class YoutubeSession(Session):
    def request(self, *args, **kwargs) -> ScraperResponse:
        kwargs["cookies"] = kwargs.get("cookies", {}) | {"SOCS": "CAESEwgDEgk0ODE3Nzk3MjQaAmVuIAEaBgiA_LyaBg"}
        return super().request(*args, **kwargs)

    @ring.lru()
    def channel_data(self, artist_url: str) -> YoutubeChannelData:
        starting_json = self.get(f"{artist_url}/about").search_json(pattern=r"ytInitialData = ({.*?});")

        result = re.findall(r'continuationCommand":{"token":"(.*?)","request":"CONTINUATION_REQUEST_TYPE_BROWSE"',
                            json.dumps(starting_json, separators=(",", ":")))
        continuation_token: str = result[-1]

        data = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20231121.08.00",
                    "originalUrl": f"{artist_url}/about",
                },
                "adSignalsInfo": {
                    "params": [],
                },
            },
            "continuation": continuation_token,
        }

        for key in ["dt", "flash", "frm", "bc", "bih", "biw", "brdim", "vis", "wgl", "ca_type",
                    "u_tz", "u_his", "u_h", "u_w", "u_ah", "u_aw", "u_cd"]:
            data["context"]["adSignalsInfo"]["params"].append({"key": key, "value": ""})  # type: ignore[index]

        json_data = self.post(
            "https://www.youtube.com/youtubei/v1/browse",
            params={
                "key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
                "prettyPrint": "false",
            },
            json=data,
        ).json()

        channel_metadata = starting_json["metadata"]["channelMetadataRenderer"]

        about_data = json_data["onResponseReceivedEndpoints"][0]["appendContinuationItemsAction"]["continuationItems"][0]
        about_data = about_data["aboutChannelRenderer"]["metadata"]["aboutChannelViewModel"]

        return YoutubeChannelData(**channel_metadata | {"links": about_data.get("links", [])})


class YoutubeChannelData(BaseModel):
    # metadata -> channelMetadataRenderer
    title: str
    description: str
    vanityChannelUrl: str

    # whatever the fuck the about data is
    links: list

    @property
    def vanity_url(self) -> Url:
        return Url.parse(self.vanityChannelUrl)

    @property
    def related_urls(self) -> list[Url]:
        urls: list[str] = []

        urls = [
            link["channelExternalLinkViewModel"]["link"]["commandRuns"][0]["onTap"]["innertubeCommand"]["commandMetadata"]["webCommandMetadata"]["url"]  # pylint: disable=line-too-long  # noqa: E501
            for link in self.links
        ]

        return [Url.parse(url) for url in urls]
