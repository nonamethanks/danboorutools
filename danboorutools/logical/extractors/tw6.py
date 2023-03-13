from bs4.element import NavigableString

from danboorutools.models.url import ArtistUrl, Url


class Tw6Url(Url):
    pass


class Tw6ArtistUrl(ArtistUrl, Tw6Url):
    user_id: int

    normalize_template = "https://tw6.jp/gallery/master/?master_id={user_id}"

    @property
    def primary_names(self) -> list[str]:
        data = self.html.select_one(".txt:has(.author) h1")
        data = [c for c in data.children if c and c.text.strip()]
        if not len(data) == 3:  # some sanity checks
            raise ValueError(self, data)
        if not data[0].text.strip().isnumeric():
            raise ValueError(self, data)
        if not isinstance(data[1], NavigableString):
            raise TypeError(self, data)

        return [data[1].strip()]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []  # not worth the hassle to extract them
