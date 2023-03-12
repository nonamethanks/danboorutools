from typing import Literal

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class SkimaUrl(Url):
    pass


class SkimaArtistUrl(ArtistUrl, SkimaUrl):
    user_id: int

    normalize_string = "https://skima.jp/profile?id={user_id}"

    @property
    def primary_names(self) -> list[str]:
        return [self.html.select_one("#profile-header h1.username").text]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        body = self.html.select_one(".panel-body")

        return [Url.parse(u) for u in extract_urls_from_string(body.text)]


class SkimaItemUrl(PostUrl, SkimaUrl):
    item_id: int

    normalize_string = "https://skima.jp/item/detail?item_id={item_id}"


class SkimaGalleryUrl(PostUrl, SkimaUrl):
    gallery_id: int

    normalize_string = "https://skima.jp/gallery?id={gallery_id}"


class SkimaImageUrl(PostAssetUrl, SkimaUrl):
    post_type: Literal["item", "gallery"]

    @property
    def full_size(self) -> str:
        if self.parsed_url.url_parts[-1].startswith("tip-") or self.parsed_url.url_parts[-1].startswith("detail-"):
            raise NotImplementedError(self)  # samples
        return self.parsed_url.raw_url
