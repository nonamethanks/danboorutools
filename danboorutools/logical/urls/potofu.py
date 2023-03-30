from danboorutools.logical.sessions.potofu import PotofuArtistData, PotofuSession
from danboorutools.models.url import ArtistUrl, Url


class PotofuUrl(Url):
    session = PotofuSession()


class PotofuArtistUrl(ArtistUrl, PotofuUrl):
    user_id: str

    normalize_template = "https://potofu.me/{user_id}"

    @property
    def artist_data(self) -> PotofuArtistData:
        return self.session.user_data(self.user_id)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.name, self.artist_data.name_en]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls
