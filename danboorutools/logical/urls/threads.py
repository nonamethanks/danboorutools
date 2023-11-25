from danboorutools.logical.sessions.threads import ThreadsArtistData, ThreadsSession
from danboorutools.models.url import ArtistUrl, PostUrl, Url


class ThreadsUrl(Url):
    session = ThreadsSession()


class ThreadsArtistUrl(ArtistUrl, ThreadsUrl):
    username: str

    normalize_template = "https://www.threads.net/@{username}"

    @property
    def artist_data(self) -> ThreadsArtistData:
        return self.session.artist_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.full_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.artist_data.username]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls


class ThreadsPostUrl(PostUrl, ThreadsUrl):
    post_id: str
    username: str

    normalize_template = "https://www.threads.net/@{username}/post/{post_id}"
