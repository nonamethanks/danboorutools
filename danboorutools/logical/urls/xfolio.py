import re

from danboorutools.models.url import ArtistUrl, Url


class XfolioUrl(Url):
    pass


class XfolioArtistUrl(ArtistUrl, XfolioUrl):
    username: str

    normalize_template = "https://xfolio.jp/portfolio/{username}"

    @property
    def related(self) -> list[Url]:
        header_el = self.html.select_one(".header--portfolio__wrapper")
        assert header_el
        header_links_els = header_el.select("a")
        assert header_links_els
        header_urls = [a["href"] for a in header_links_els]

        button_urls = [a["href"] for a in self.html.select("a.button")]

        if not header_urls and not button_urls:
            raise NotImplementedError(self)

        urls = [Url.parse(u) for u in header_urls + button_urls if u.startswith("http")]

        return list(dict.fromkeys(u for u in urls if u != self))

    @property
    def primary_names(self) -> list[str]:
        meta_description_el = self.html.select_one("meta[property='og:description']")
        assert meta_description_el
        content = meta_description_el["content"]
        match = re.search(r"/creator:([\S]*)", content)   # pyright: ignore[reportGeneralTypeIssues]
        assert match
        name = match.groups()[0]
        return [name.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]


class XfolioPostUrl(ArtistUrl, XfolioUrl):
    username: str
    post_id: int

    normalize_template = "https://xfolio.jp/portfolio/{username}/works/{post_id}"
