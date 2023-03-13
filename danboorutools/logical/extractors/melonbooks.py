from danboorutools.logical.sessions.melonbooks import MelonbooksSession
from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class MelonbooksUrl(Url):
    session = MelonbooksSession()


class MelonbooksProductUrl(PostUrl, MelonbooksUrl):
    product_id: int

    normalize_template = "https://www.melonbooks.co.jp/detail/detail.php?product_id={product_id}"


class MelonbooksCircleUrl(ArtistUrl, MelonbooksUrl):
    circle_id: int

    normalize_template = "https://www.melonbooks.co.jp/circle/index.php?circle_id={circle_id}"

    @property
    def primary_names(self) -> list[str]:
        pen_names = self.html.find("th", string="ペンネーム").parent.select_one("td").text.split()
        return [p.strip("()") for p in pen_names]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        pixiv_url = self.html.find("th", string="PixivID").parent.select_one("td").text.split()
        twitter_url = self.html.find("th", string="Twitter URL").parent.select_one("td").text.split()

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
