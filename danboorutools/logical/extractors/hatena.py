from __future__ import annotations

import re

from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, InfoUrl, PostAssetUrl, PostUrl, Url


class HatenaUrl(Url):
    pass


class HatenaFotolifeArtistUrl(ArtistUrl, HatenaUrl):
    username: str

    normalize_template = "https://f.hatena.ne.jp/{username}/"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return [Url.build(HatenaProfileUrl, username=self.username)]


class HatenaFotolifePostUrl(PostUrl, HatenaUrl):
    username: str
    post_id: int

    normalize_template = "https://f.hatena.ne.jp/{username}/{post_id}"


class HatenaProfileUrl(InfoUrl, HatenaUrl):
    username: str

    normalize_template = "https://profile.hatena.ne.jp/{username}/"

    @property
    def primary_names(self) -> list[str]:
        header = self.html.select_one("#user-header-body > h1")
        name_match = re.match(r"^(.*)'s Profile$", header.text.strip())
        if not name_match:
            raise NotImplementedError(self, header)
        if self.username == (found_name := name_match.groups()[0]):
            return []
        return [found_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        urls = [el["href"] for el in self.html.select("#sidebar .hatena-modulebody .medals a")]

        urls += [el["href"] for el in self.html.select("#main .profile.addresslist a")]

        return [u for u in dict.fromkeys(map(Url.parse, urls)) if u != self]


class HatenaUgomemoUrl(InfoUrl, HatenaUrl):
    user_id: str

    normalize_template = "https://ugomemo.hatena.ne.jp/{user_id}/"

    is_deleted = True


class HatenaBlogUrl(ArtistUrl, HatenaUrl):
    username: str
    domain: str

    normalize_template = "https://{username}.{domain}"


class HatenaBlogPostUrl(PostUrl, HatenaUrl):
    username: str
    domain: str
    post_id: str
    post_date_str: str

    normalize_template = "https://{username}.{domain}/entry/{post_date_str}/{post_id}"


class HatenaImageUrl(PostAssetUrl, HatenaUrl):
    pass


class HatenaArtistImageUrl(GalleryAssetUrl, HatenaUrl):
    username: str
