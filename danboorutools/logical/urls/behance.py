from danboorutools.logical.sessions.behance import BehanceSession, BehanceUserData
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class BehanceUrl(Url):
    session = BehanceSession()


class BehanceArtistUrl(ArtistUrl, BehanceUrl):
    username: str

    normalize_template = "https://www.behance.net/{username}"

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.display_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls

    @property
    def artist_data(self) -> BehanceUserData:
        return self.session.user_data(self.username)


class BehancePostUrl(PostUrl, BehanceUrl):
    post_id: int
    title: str

    normalize_template = "https://www.behance.net/gallery/{post_id}/{title}"


class BehanceImageUrl(PostAssetUrl, BehanceUrl):
    ...
