from danboorutools.logical.sessions.vgen import VgenArtistData, VgenSession
from danboorutools.models.url import ArtistUrl, PostUrl, Url


class VgenUrl(Url):
    session = VgenSession()


class VgenArtistUrl(ArtistUrl, VgenUrl):
    username: str

    normalize_template = "https://vgen.co/{username}"

    @property
    def artist_data(self) -> VgenArtistData:
        return self.session.artist_data(username=self.username)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.displayName]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls


class VgenPostUrl(PostUrl, VgenUrl):
    username: str
    post_title: str
    post_id: str

    normalize_template = "https://vgen.co/{username}/portfolio/showcase/{post_title}/{post_id}"
