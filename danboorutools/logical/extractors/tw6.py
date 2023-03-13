from bs4.element import NavigableString

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


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


class Tw6PostUrl(PostUrl, Tw6Url):
    post_id: int

    normalize_template = "https://tw6.jp/gallery/?id={user_id}"


class Tw6ImageUrl(PostAssetUrl, Tw6Url):
    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


class Tw6CharacterUrl(PostUrl, Tw6Url):
    character_id: str  # the fuck is this adoptable bullshit

    normalize_template = "https://tw6.jp/character/status/{character_id}"
