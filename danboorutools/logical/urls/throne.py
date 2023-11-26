from bs4 import Tag

from danboorutools.models.url import ArtistUrl, PostUrl, Url


class ThroneUrl(Url):
    ...


class ThroneArtistUrl(ArtistUrl, ThroneUrl):
    username: str

    normalize_template = "https://throne.com/{username}"

    @property
    def _info_container(self) -> Tag:
        avatar = self.html.select_one(".chakra-avatar")
        assert avatar
        parent = avatar.find_parent("div", class_="chakra-container")
        assert parent
        return parent

    @property
    def primary_names(self) -> list[str]:
        name = self._info_container.select_one(".chakra-heading")
        assert name
        return [name.text]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        link_els = self._info_container.select("a.chakra-button")
        assert link_els
        return [Url.parse(link_el["href"]) for link_el in link_els]  # pyright: ignore[reportGeneralTypeIssues]


class ThronePostUrl(PostUrl, ThroneUrl):
    post_id: str
    username: str

    normalize_template = "https://throne.com/{username}/item/{post_id}"
