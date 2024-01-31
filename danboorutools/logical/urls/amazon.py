from danboorutools.models.url import ArtistUrl, PostUrl, RedirectUrl, Url


class AmazonUrl(Url):
    ...


class AmazonAuthorUrl(ArtistUrl, AmazonUrl):
    author_id: str
    subsite: str

    normalize_template = "https://www.amazon.{subsite}/stores/author/{author_id}"

    @property
    def related(self) -> list[Url]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one("[class^=AuthorSubHeader__author-subheader__name__]"))
        return [name_el.text.strip()]


class AmazonItemUrl(PostUrl, AmazonUrl):
    item_id: str
    subsite: str

    normalize_template = "https://www.amazon.{subsite}/dp/{item_id}"


class AmazonShortenerUrl(RedirectUrl, AmazonUrl):
    shortener_id: str

    normalize_template = "https://amzn.to/{shortener_id}"
