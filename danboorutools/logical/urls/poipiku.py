import re

from danboorutools.logical.sessions.poipiku import PoipikuSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class PoipikuUrl(Url):
    session = PoipikuSession()


class PoipikuPostUrl(PostUrl, PoipikuUrl):
    user_id: int
    post_id: int

    normalize_template = "https://poipiku.com/{user_id}/{post_id}.html"


class PoipikuArtistUrl(ArtistUrl, PoipikuUrl):
    user_id: int

    normalize_template = "https://poipiku.com/{user_id}/"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one(".UserInfoUserName"))
        return [name_el.text]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        user_profile = str(self.html.select_one(".UserInfoProfile"))
        return [Url.parse(u) for u in extract_urls_from_string(user_profile)]

    def subscribe(self) -> None:
        self.session.subscribe(self.user_id)

    def unsubscribe(self) -> None:
        self.session.unsubscribe(self.user_id)


class PoipikuHeaderImageUrl(GalleryAssetUrl, PoipikuUrl):
    user_id: int
    image_hash: str
    image_id: int

    @property
    def full_size(self) -> str:
        original_url = re.sub(r"(\.\w+)_\d+\.\w+$", "\\1", self.parsed_url.raw_url)
        return original_url

    @property
    def gallery(self) -> PoipikuArtistUrl:
        return PoipikuArtistUrl.build(user_id=self.user_id)


class PoipikuImageUrl(PostAssetUrl, PoipikuUrl):
    user_id: int
    post_id: int
    image_hash: str | None
    image_id: int | None

    @property
    def full_size(self) -> str:
        original_filename = re.sub(r"(\.\w+)_\d+\.\w+$", "\\1", self.parsed_url.filename)
        return "https://img-org.poipiku.com/" + "/".join(self.parsed_url.url_parts[:-1]) + "/" + original_filename
