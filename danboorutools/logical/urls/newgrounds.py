from __future__ import annotations

import re
from datetime import datetime
from functools import cached_property

from danboorutools.logical.sessions.newgrounds import NewgroundsSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.time import datetime_from_string


class NewgroundsUrl(Url):
    session = NewgroundsSession()


class NewgroundsPostUrl(PostUrl, NewgroundsUrl):
    username: str
    title: str

    normalize_template = "https://www.newgrounds.com/art/view/{username}/{title}"

    def _extract_assets(self) -> list[str]:
        assets: list[str] = [img["src"] for img in self.html.select(".image img")]
        extra_images = self.html.select("#author_comments img[data-user-image='1']")
        for image_el in extra_images:
            for src_type in ["src", "data-smartload-src"]:
                try:
                    image_str = image_el[src_type]
                except KeyError:
                    pass
                else:
                    if image_str.startswith("//"):
                        image_str = f"https:{image_str}"
                    assets.append(image_str)
        return assets

    @cached_property
    def score(self) -> int:
        return int(self.html.select_one("meta[itemprop='ratingCount']")["content"])

    @cached_property
    def created_at(self) -> datetime:
        datetime_str = self.html.select_one("meta[itemprop='datePublished']")["content"]
        return datetime_from_string(datetime_str)

    @property
    def gallery(self) -> NewgroundsArtistUrl:
        return NewgroundsArtistUrl.build(NewgroundsArtistUrl, username=self.username)


class NewgroundsDumpUrl(PostUrl, NewgroundsUrl):
    dump_id: str

    normalize_template = "https://www.newgrounds.com/dump/item/{dump_id}"


class NewgroundsVideoPostUrl(PostUrl, NewgroundsUrl):
    video_id: int

    normalize_template = "https://www.newgrounds.com/portal/view/{video_id}"


class NewgroundsArtistUrl(ArtistUrl, NewgroundsUrl):
    username: str

    normalize_template = "https://{username}.newgrounds.com"


class NewgroundsAssetUrl(PostAssetUrl, NewgroundsUrl):
    username: str | None
    title: str | None

    @property
    def full_size(self) -> str:
        if self.parsed_url.hostname == "uploads.ungrounded.net":
            return re.sub(r"\.\d+p\.", ".", self.parsed_url.url_without_query)
        elif self.parsed_url.url_parts[0] in ("images", "comments"):
            return self.parsed_url.url_without_query
        else:
            raise NotImplementedError
