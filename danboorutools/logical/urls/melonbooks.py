from __future__ import annotations

from functools import cached_property

from danboorutools.logical.sessions.melonbooks import MelonbooksSession
from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class MelonbooksUrl(Url):
    session = MelonbooksSession()


class MelonbooksProductUrl(PostUrl, MelonbooksUrl):
    product_id: int

    normalize_template = "https://www.melonbooks.co.jp/detail/detail.php?product_id={product_id}"

    @cached_property
    def gallery(self) -> MelonbooksAuthorUrl:
        assert (artists_el := self.html.find("th", string="作家名"))
        artists = artists_el.parent.select("td a:not(.fa-heart)")
        if len(artists) != 1:
            raise NotImplementedError(self, artists)

        parsed = MelonbooksAuthorUrl.parse_and_assert(artists[0]["href"])
        return parsed


class MelonbooksCircleUrl(ArtistUrl, MelonbooksUrl):
    circle_id: int

    normalize_template = "https://www.melonbooks.co.jp/circle/index.php?circle_id={circle_id}"

    @property
    def primary_names(self) -> list[str]:
        assert (pen_names_el := self.html.find("th", string="ペンネーム"))
        pen_names = pen_names_el.parent.select_one("td").text.split()
        return [p.strip("()") for p in pen_names]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        assert (pixiv_id_el := self.html.find("th", string="PixivID"))
        pixiv_url = pixiv_id_el.parent.select_one("td").text.split()
        assert (twitter_url_el := self.html.find("th", string="X(Twitter) URL"))
        twitter_url = twitter_url_el.parent.select_one("td").text.split()

        return [
            Url.parse(u.strip())
            for u in pixiv_url + twitter_url
            if u.strip()
        ]


class MelonbooksAuthorUrl(ArtistUrl, MelonbooksUrl):
    artist_name: str

    normalize_template = "https://www.melonbooks.co.jp/search/search.php?name={artist_name}&text_type=author"


class MelonbooksCornerUrl(ArtistAlbumUrl, MelonbooksUrl):
    corner_id: int

    normalize_template = "https://www.melonbooks.co.jp/corner/detail.php?corner_id={corner_id}"


class MelonbooksImageUrl(PostAssetUrl, MelonbooksUrl):
    filename: str | None

    @property
    def full_size(self) -> str:
        if self.filename:
            return f"https://www.melonbooks.co.jp/resize_image.php?image={self.filename}"
        return self.parsed_url.raw_url
