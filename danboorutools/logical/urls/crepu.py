from danboorutools.logical.sessions.crepu import CrepuArtistData, CrepuSession
from danboorutools.models.url import ArtistUrl, PostUrl, Url


class CrepuUrl(Url):
    session = CrepuSession()


class CrepuArtistUrl(ArtistUrl, CrepuUrl):
    normalize_template = "https://crepu.net/user/{username}"

    username: str

    @property
    def artist_data(self) -> CrepuArtistData:
        return self.session.artist_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.user_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.artist_data.user_crepu_id]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls



class CrepuPostUrl(PostUrl, CrepuUrl):
    normalize_template = "https://crepu.net/post/{post_id}"
    post_id: int
