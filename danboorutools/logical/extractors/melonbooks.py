from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class MelonbooksUrl(Url):
    pass


class MelonbooksProductUrl(PostUrl, MelonbooksUrl):
    product_id: int

    normalize_string = "https://www.melonbooks.co.jp/detail/detail.php?product_id={product_id}"


class MelonbooksCircleUrl(ArtistUrl, MelonbooksUrl):
    circle_id: int

    normalize_string = "https://www.melonbooks.co.jp/circle/index.php?circle_id={circle_id}"


class MelonbooksAuthorUrl(ArtistUrl, MelonbooksUrl):
    artist_name: str

    normalize_string = "https://www.melonbooks.co.jp/search/search.php?name={artist_name}&text_type=author"


class MelonbooksCornerUrl(ArtistAlbumUrl, MelonbooksUrl):
    corner_id: int

    normalize_string = "https://www.melonbooks.co.jp/corner/detail.php?corner_id={corner_id}"


class MelonbooksImageUrl(PostAssetUrl, MelonbooksUrl):
    filename: str | None

    @property
    def full_size(self) -> str:
        if self.filename:
            return f"https://www.melonbooks.co.jp/resize_image.php?image={self.filename}"
        return self.parsed_url.raw_url
