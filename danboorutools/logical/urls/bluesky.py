import re

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class BskyUrl(Url):
    ...


class BlueskyArtistUrl(ArtistUrl, BskyUrl):
    username: str

    normalize_template = "https://bsky.app/profile/{username}"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one("meta[property='og:title']"))
        assert (match := re.match(rf"^(.*)\(@{self.username}\)$", name_el.attrs["content"]))
        return list(match.groups())

    @property
    def secondary_names(self) -> list[str]:
        return [self.username.removesuffix(".bsky.social")]

    @property
    def related(self) -> list[Url]:
        assert (description_el := self.html.select_one("meta[property='og:description']"))
        return list(map(Url.parse, extract_urls_from_string(description_el.attrs["content"])))


class BlueskyPostUrl(PostUrl, BskyUrl):
    post_id: str
    username: str

    normalize_template = "https://bsky.app/profile/{username}/post/{post_id}"


class BskyImageUrl(PostAssetUrl, BskyUrl):
    ...
