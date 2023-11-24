from danboorutools.logical.sessions.soundcloud import SoundcloudArtistData, SoundcloudSession
from danboorutools.models.url import ArtistUrl, GalleryUrl, PostUrl, RedirectUrl, Url


class SoundcloudUrl(Url):
    session = SoundcloudSession()


class SoundcloudArtistUrl(ArtistUrl, SoundcloudUrl):
    username: str

    normalize_template = "https://soundcloud.com/{username}"

    @property
    def artist_data(self) -> SoundcloudArtistData:
        return self.session.artist_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.username]

    @property
    def secondary_names(self) -> list[str]:
        if self.username.startswith("user-"):
            return []

        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class SoundcloudPostUrl(PostUrl, SoundcloudUrl):
    post_id: str
    username: str

    normalize_template = "https://soundcloud.com/{username}/{post_id}"


class SoundcloudPostSetUrl(GalleryUrl, SoundcloudUrl):
    post_id: str
    username: str

    normalize_template = "https://soundcloud.com/{username}/sets/{post_id}"


class SoundcloudArtistRedirectUrl(RedirectUrl, SoundcloudUrl):
    redirect_id: str

    normalize_template = "https://on.soundcloud.com/{redirect_id}"
