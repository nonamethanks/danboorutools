from functools import cached_property

from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class AfdianUrl(Url):
    pass


class AfdianPostUrl(PostUrl, AfdianUrl):
    post_id: str

    normalize_template = "https://afdian.net/p/{post_id}"


class AfdianArtistUrl(ArtistUrl, AfdianUrl):
    username: str

    normalize_template = "https://afdian.net/a/{username}"

    @property
    def primary_names(self) -> list[str]:
        return [self._user_data["name"]]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        creator_detail = self._user_data["creator"]["detail"]
        return [self.parse(url) for url in extract_urls_from_string(creator_detail)]

    @cached_property
    def _user_data(self) -> dict:
        response = self.session.get_json_cached(f"https://afdian.net/api/user/get-profile-by-slug?url_slug={self.username}")
        return response["data"]["user"]


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
