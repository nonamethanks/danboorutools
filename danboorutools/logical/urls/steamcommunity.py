from danboorutools.models.url import ArtistUrl, PostUrl, Url


class SteamUrl(Url):
    ...


class SteamCommunityProfileUrl(ArtistUrl, SteamUrl):
    username: str | None = None
    user_id: int | None = None

    normalize_template = "https://steamcommunity.com/id/{username}"

    @classmethod
    def normalize(cls, **kwargs) -> str:
        if user_id := kwargs.get("user_id"):
            return f"https://steamcommunity.com/profiles/{user_id}"
        elif username := kwargs.get("username"):
            return f"https://steamcommunity.com/id/{username}"
        else:
            raise NotImplementedError

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one(".profile_header .actual_persona_name"))
        return [name_el.text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        if self.username:
            return [self.username]
        return []

    @property
    def related(self) -> list[Url]:
        assert (profile_el := self.html.select_one(".profile_summary"))
        links = profile_el.select(".bb_link")

        return [Url.parse(link["href"]) for link in links]  # pyright: ignore[reportGeneralTypeIssues]


class SteamcommunityFileUrl(PostUrl, SteamUrl):
    file_id: int

    normalize_template = "https://steamcommunity.com/sharedfiles/filedetails/?id={file_id}"
