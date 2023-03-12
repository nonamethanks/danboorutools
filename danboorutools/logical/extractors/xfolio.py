from danboorutools.models.url import ArtistUrl, Url


class XfolioUrl(Url):
    pass


class XfolioArtistUrl(ArtistUrl, XfolioUrl):
    username: str

    normalize_string = "https://xfolio.jp/portfolio/{username}"

    @property
    def related(self) -> list[Url]:
        header_urls = [a["href"] for a in self.html.select_one(".header--portfolio__wrapper").select("a")]

        button_urls = [a["href"] for a in self.html.select("a.button")]

        if not header_urls and not button_urls:
            raise NotImplementedError(self)

        urls = [Url.parse(u) for u in header_urls + button_urls if u.startswith("http")]

        return list(dict.fromkeys(u for u in urls if u != self))

    @property
    def primary_names(self) -> list[str]:
        return []  # too complex to split the blog title from the actual nmae

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]


class XfolioPostUrl(ArtistUrl, XfolioUrl):
    username: str
    post_id: int

    normalize_string = "https://xfolio.jp/portfolio/{username}/works/{post_id}"
