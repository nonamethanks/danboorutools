from __future__ import annotations

import re

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url, parse_list
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class LitLinkSession(Session):
    def artist_data(self, username: str) -> LitLinkArtistData:
        artist_url = f"https://lit.link/{username}"
        response = self.get(artist_url)

        if response.html.select_one("title").text.strip() == "Not Found lit.link":
            raise DeadUrlError(response)

        artist_data = response.search_json(
            pattern=r"self.__next_f.push\(.*?({.*urlPath.*}).*?\)",
            post_process=lambda x: re.sub(r'\\+"', '\\"', x.replace('\\"', '"')),
        )
        artist_data = artist_data["children"][-1]["profile"]
        return LitLinkArtistData(**artist_data)


class LitLinkArtistData(BaseModel):
    name: str
    profileLinks: list[dict]

    @property
    def related_urls(self) -> list[Url]:
        urls: list[str] = []
        for profile_link in self.profileLinks:
            match profile_link["profileLinkType"]:
                case "button":
                    if profile_link["buttonLink"]["urlType"] == "email":
                        continue
                    urls += [profile_link["buttonLink"]["url"]]
                case "margin_block":
                    pass
                case "image":
                    urls += [image_data["url"] for image_data in profile_link["imageLink"]["profileImages"]]
                case "movie":
                    urls += [profile_link["movieLink"]["url"]]
                case "text":
                    if (title := profile_link["textLink"]["title"]):
                        urls += extract_urls_from_string(title)
                    if (desc := profile_link["textLink"]["description"]):
                        urls += extract_urls_from_string(desc)
                case _:
                    raise NotImplementedError(profile_link)

        return list({Url.parse(u) for u in urls if u and u.startswith("http")})
