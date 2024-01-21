from datetime import datetime
from functools import cached_property
from posixpath import ismount

from danboorutools.logical.sessions.artstation import ArtstationArtistData, ArtstationPostData, ArtstationSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class ArtStationUrl(Url):
    session = ArtstationSession()


class ArtStationOldPostUrl(RedirectUrl, ArtStationUrl):
    # https://www.artstation.com/artwork/cody-from-sf  # (old; redirects to https://www.artstation.com/artwork/3JJA)
    post_title: str

    normalize_template = "https://www.artstation.com/artwork/{post_title}"


class ArtStationArtistUrl(ArtistUrl, ArtStationUrl):
    username: str

    normalize_template = "https://www.artstation.com/{username}"

    @property
    def artist_data(self) -> ArtstationArtistData:
        return self.session.artist_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        return [self.artist_data.full_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        return [u for u in self.artist_data.related_urls if u != self]


class ArtStationPostUrl(PostUrl, ArtStationUrl):
    post_id: str
    username: str | None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        if username := kwargs.get("username"):
            return f"https://{username}.artstation.com/projects/{post_id}"
        else:
            return f"https://www.artstation.com/artwork/{post_id}"

    @property
    def post_data(self) -> ArtstationPostData:
        return self.session.post_data(self.post_id)

    def _extract_assets(self) -> list[str]:
        return [asset["image_url"] for asset in self.post_data.assets if asset["has_image"]]

    @cached_property
    def gallery(self) -> ArtStationArtistUrl:
        username = self.username or self.post_data.user["username"]
        return ArtStationArtistUrl.build(username=username)

    @cached_property
    def created_at(self) -> datetime:
        return self.post_data.created_at

    @cached_property
    def score(self) -> int:
        return self.post_data.likes_count


class ArtStationImageUrl(PostAssetUrl, ArtStationUrl):
    filename: str
    asset_type: str
    asset_subdirs: str

    post = None
    gallery = None

    @property
    def full_size(self) -> str:
        if self.parsed_url.subdomain == "cdn-animation":
            return f"https://cdn-animation.artstation.com/p/{self.asset_type}/{self.asset_subdirs}/{self.filename}"
        else:
            return f"https://cdn.artstation.com/p/assets/{self.asset_type}/images/{self.asset_subdirs}/4k/{self.filename}"
        # https://cdn.artstation.com/p/assets/covers/images/007/262/828/4k/monica-kyrie-1.jpg this is actually wrong, the original is "original"
        # idk how to properly fix this


class ArtStationMarketplacePostUrl(PostUrl, ArtStationUrl):
    post_id: str

    normalize_template = "https://www.artstation.com/marketplace/p/{post_id}"
