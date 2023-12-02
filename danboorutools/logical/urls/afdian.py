from functools import cached_property

from danboorutools.logical.sessions.afdian import AfdianArtistData, AfdianSession
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class AfdianUrl(Url):
    session = AfdianSession()


class AfdianPostUrl(PostUrl, AfdianUrl):
    post_id: str

    normalize_template = "https://afdian.net/p/{post_id}"


class AfdianArtistUrl(ArtistUrl, AfdianUrl):
    username: str

    normalize_template = "https://afdian.net/a/{username}"

    @cached_property
    def artist_data(self) -> AfdianArtistData:
        return self.session.artist_data(username=self.username)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls


class AfdianImageUrl(PostAssetUrl, AfdianUrl):
    user_id: str

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query


class AfdianArtistImageUrl(GalleryAssetUrl, AfdianUrl):
    user_id: str

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query
