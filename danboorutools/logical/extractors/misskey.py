from danboorutools.logical.sessions.misskey import MisskeySession, MisskeyUserData
from danboorutools.models.url import ArtistUrl, Url


class MisskeyUrl(Url):
    session = MisskeySession()


class MisskeyUserUrl(ArtistUrl, MisskeyUrl):
    username: str

    normalize_template = "https://misskey.io/@{username}"

    @property
    def artist_data(self) -> MisskeyUserData:
        return self.session.artist_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        if self.artist_data.name:
            return [self.artist_data.name]
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls
