from functools import cached_property

from atproto_client.models.app.bsky.actor.defs import ProfileViewDetailed

from danboorutools.logical.sessions.bluesky import BskySession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class BskyUrl(Url):
    session = BskySession()


class BlueskyArtistUrl(ArtistUrl, BskyUrl):
    username: str

    normalize_template = "https://bsky.app/profile/{username}"

    @cached_property
    def artist_data(self) -> ProfileViewDetailed:
        return self.session.api.get_profile(self.username)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.display_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username.removesuffix(".bsky.social")]

    @property
    def related(self) -> list[Url]:
        description = self.artist_data.description

        return list(map(Url.parse, extract_urls_from_string(description)))


class BlueskyPostUrl(PostUrl, BskyUrl):
    post_id: str
    username: str

    normalize_template = "https://bsky.app/profile/{username}/post/{post_id}"


class BskyImageUrl(PostAssetUrl, BskyUrl):
    ...
