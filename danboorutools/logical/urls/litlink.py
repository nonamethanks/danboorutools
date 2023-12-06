from danboorutools.logical.sessions.litlink import LitLinkArtistData, LitLinkSession
from danboorutools.models.url import InfoUrl, Url


class LitlinkUrl(InfoUrl):
    session = LitLinkSession()

    username: str
    normalize_template = "https://lit.link/{username}"

    @property
    def artist_data(self) -> LitLinkArtistData:
        return self.session.artist_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        return [self.artist_data.name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        return self.artist_data.related_urls
