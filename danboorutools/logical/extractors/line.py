from danboorutools.models.url import ArtistUrl, PostUrl, Url


class LineUrl(Url):
    ...


class LineArtistUrl(ArtistUrl, LineUrl):
    artist_id: int

    normalize_string = "https://store.line.me/stickershop/author/{artist_id}"

    @property
    def is_deleted(self) -> bool:
        if self.html.select("[data-test='author-item']"):
            return False

        if self.html.select("[data-test='no-item-available-text']"):
            return False

        raise NotImplementedError(self)

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        raise NotImplementedError(self)

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []


class LinePostUrl(PostUrl, LineUrl):
    product_id: int

    normalize_string = "https://store.line.me/stickershop/product/{product_id}"
