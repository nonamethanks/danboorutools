from danboorutools.logical.sessions.linktree import LinktreeSession
from danboorutools.models.url import InfoUrl, Url


class LinktreeUrl(InfoUrl):
    session = LinktreeSession()

    username: str

    normalize_template = "https://linktr.ee/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return self.session.artist_data(self.username).related
