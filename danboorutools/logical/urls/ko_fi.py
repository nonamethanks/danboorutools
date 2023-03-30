from datetime import datetime
from functools import cached_property

from bs4 import BeautifulSoup

from danboorutools.logical.sessions.ko_fi import KoFiSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.time import datetime_from_string


class KoFiUrl(Url):
    session = KoFiSession()


class KoFiArtistUrl(ArtistUrl, KoFiUrl):
    username: str

    normalize_template = "https://ko-fi.com/{username}"


class KoFiPostUrl(PostUrl, KoFiUrl):
    post_id: str

    normalize_template = "https://ko-fi.com/i/{post_id}"

    @cached_property
    def html(self) -> BeautifulSoup:
        return self.session.get_html(f"https://ko-fi.com/Gallery/LoadGalleryItem?galleryItemId={self.post_id}")

    def _extract_assets(self) -> list[str]:
        if self.html.select(".label-hires"):
            raise NotImplementedError(self)
        images = [
            el["src"].replace("/post/", "/display/")
            for el in self.html.select("img.gallery-image")
        ]
        return list(dict.fromkeys(images))

    @cached_property
    def created_at(self) -> datetime:
        asset_date = self.assets[0].created_at
        assert asset_date
        return asset_date


class KofiShopPostUrl(PostUrl, KoFiUrl):
    shop_id: str

    normalize_template = "https://ko-fi.com/s/{shop_id}"


class KoFiImageUrl(PostAssetUrl, KoFiUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query.replace("/post/", "/display/")

    @cached_property
    def created_at(self) -> datetime:
        last_modified = self.session.head(self.full_size).headers["Last-Modified"]
        return datetime_from_string(last_modified)
