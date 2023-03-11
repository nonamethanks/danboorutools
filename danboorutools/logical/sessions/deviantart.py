from __future__ import annotations

import json
import re

from danboorutools.logical.extractors.twitter import TwitterArtistUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, memoize

data_pattern = re.compile(r"window.__INITIAL_STATE__ = JSON.parse\(\"(.*)\"\);")


class DeviantartSession(Session):
    @memoize
    def user_data(self, username: str) -> DeviantartUserData:
        html = self.get_html(f"https://www.deviantart.com/{username}")
        script = next(el.string for el in html.select("script") if el.string and "window.__INITIAL_STATE__ = JSON.parse" in el.string)
        match = data_pattern.search(script)
        if not match:
            raise NotImplementedError(username)

        parsable_json = match.groups()[0].encode("utf-8").decode("unicode_escape")
        parsed_json = json.loads(parsable_json)

        about_data, = (module for module in parsed_json["modules"].values() if module["type"] == "about")

        return DeviantartUserData(**about_data["moduleData"])


class DeviantartUserData(BaseModel):
    username: str
    website: str
    twitterUsername: str | None
    textContent: dict
    socialLinks: list

    @property
    def related_urls(self) -> list[Url]:
        urls = [Url.parse(data["value"]) for data in self.socialLinks]

        if self.twitterUsername:
            urls += [Url.build(TwitterArtistUrl, username=self.twitterUsername)]

        if self.website:
            website = self.website if self.website.startswith("http") else f"https://{self.website}"
            urls += [Url.parse(website)]

        if self.textContent:
            data = json.loads(self.textContent["html"]["markup"])
            for entity in data["entityMap"].values():
                if entity["type"] != "LINK":
                    raise NotImplementedError(entity)
                urls += [Url.parse(entity["data"]["url"])]

        return list(dict.fromkeys(urls))
