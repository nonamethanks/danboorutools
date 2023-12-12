from danboorutools.models.url import ArtistUrl, PostUrl, Url


class TaittsuuUrl(Url):
    ...


class TaittsuuArtistUrl(ArtistUrl, TaittsuuUrl):
    username: str

    normalize_template = "https://taittsuu.com/users/{username}"

    @property
    def primary_names(self) -> list[str]:
        element = self.html.select_one("#profilePanel .profile-user-name-value")
        if element:
            return [element.text.strip()]
        raise NotImplementedError(self)

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        urls = self.html.select("#profilePanel .profile-url a")
        return [Url.parse(url_el["href"]) for url_el in urls]


class TaittsuuPostUrl(PostUrl, TaittsuuUrl):
    post_id: int
    username: str

    normalize_template = "https://taittsuu.com/users/{username}/status/{post_id}"
