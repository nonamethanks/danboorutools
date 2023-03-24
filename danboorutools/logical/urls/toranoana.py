from __future__ import annotations

import re
from urllib.parse import urljoin

from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class ToranoanaUrl(Url):
    pass


class ToranoanaItemUrl(PostUrl, ToranoanaUrl):
    item_id: str
    subdirs: str
    subsite: str

    normalize_template = "https://{subsite}.toranoana.jp/{subdirs}/item/{item_id}/"

    @property
    def gallery(self) -> ToranoanaArtistUrl:
        authors = self.html.select(".product-detail-spec a[name='spec-actor']")
        if len(authors) != 1:
            raise NotImplementedError(self, authors)

        parsed = Url.parse(urljoin(f"https://{self.parsed_url.hostname}", authors[0]["href"]))
        assert isinstance(parsed, ToranoanaArtistUrl)
        return parsed


class ToranoanaCircleUrl(ArtistUrl, ToranoanaUrl):
    circle_id: str
    subdirs: str
    subsite: str

    normalize_template = "https://{subsite}.toranoana.jp/{subdirs}/circle/{circle_id}/all/"


class ToranoanaArtistUrl(ArtistUrl, ToranoanaUrl):
    artist_type: str
    artist_name: str
    subdirs: str
    subsite: str

    normalize_template = "https://{subsite}.toranoana.jp/{subdirs}/app/catalog/list?{artist_type}={artist_name}"


class ToranoanaOldAuthorUrl(ArtistUrl, ToranoanaUrl):
    is_deleted = True

    normalizable = False


class ToranoanaOldCircleUrl(ArtistUrl, ToranoanaUrl):
    is_deleted = True

    normalizable = False


class ToranoanaDojinSeriesUrl(ArtistAlbumUrl, ToranoanaUrl):
    dojin_slug: str

    normalize_template = "http://www.toranoana.jp/info/dojin/{dojin_slug}/"


class ToranoanaImageUrl(PostAssetUrl, ToranoanaUrl):
    post_id: str
    page: int

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url.replace("_thumb", "")


class ToranoanaWebcomicPageUrl(PostAssetUrl, ToranoanaUrl):
    publisher: str
    webcomic_title: str
    webcomic_entry: str

    @property
    def full_size(self) -> str:
        return re.sub(r"\.\w+$", ".html", self.parsed_url.raw_url.replace("tobira.jpg", "01.jpg"))
