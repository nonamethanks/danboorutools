from __future__ import annotations

import json
import re

import ring

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string

JSON_DATA_PATTERN = re.compile(r"bootstrap, ({.*?)\);\s", re.DOTALL)


class PatreonSession(Session):
    def artist_data(self, url: str) -> PatreonArtistData:
        request = self.get(url, cached=True)
        json_data = JSON_DATA_PATTERN.search(request.text)
        if not json_data:
            raise NotImplementedError(url)
        parsed_data = json.loads(json_data.groups()[0])
        return PatreonArtistData(**parsed_data["campaign"])


class PatreonArtistData(BaseModel):
    included: list[dict]
    data: dict

    @property
    def name(self) -> str:
        return self.data["attributes"]["name"]

    @property
    def username(self) -> str:
        return self.data["attributes"]["vanity"]

    @property
    def related_urls(self) -> list[Url]:
        urls = extract_urls_from_string(self.data["attributes"]["summary"])

        for included in self.included:
            if included["type"].startswith("reward"):
                continue
            if included["type"] in ("user", "post_aggregation", "goal"):
                continue
            if included["type"] == "social-connection":
                urls += [included["attributes"]["external_profile_url"]]
                continue
            raise NotImplementedError(included)

        return [Url.parse(u) for u in urls]
