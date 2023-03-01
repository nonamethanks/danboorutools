import re

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PoipikuUrl(Url):
    pass


class PoipikuPostUrl(PostUrl, PoipikuUrl):
    user_id: int
    post_id: int

    normalize_string = "https://poipiku.com/{user_id}/{post_id}.html"


class PoipikuArtistUrl(ArtistUrl, PoipikuUrl):
    user_id: int

    normalize_string = "https://poipiku.com/{user_id}/"


class PoipikuImageUrl(PostAssetUrl, PoipikuUrl):
    user_id: int
    post_id: int
    image_hash: str | None
    image_id: int | None

    @property
    def full_size(self) -> str:
        original_filename = re.sub(r"(\.\w+)_\d+\.\w+$", "\\1", self.parsed_url.filename)
        return "https://img-org.poipiku.com/" + "/".join(self.parsed_url.url_parts[:-1]) + "/" + original_filename
