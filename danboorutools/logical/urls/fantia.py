import re
from functools import cached_property

from danboorutools.logical.sessions.fantia import FantiaPostData, FantiaSession
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class FantiaUrl(Url):
    session = FantiaSession()


class FantiaPostUrl(PostUrl, FantiaUrl):
    post_id: int
    post_type: str

    normalize_template = "https://fantia.jp/{post_type}/{post_id}"

    @cached_property
    def post_data(self) -> FantiaPostData:
        if self.post_type == "posts":
            return self.session.get_post_data(self.post_id)
        else:
            raise NotImplementedError(self)


class FantiaFanclubUrl(ArtistUrl, FantiaUrl):
    fanclub_id: int | None
    fanclub_name: str | None

    @classmethod
    def normalize(cls, **url_properties) -> str:
        if fanclub_id := url_properties["fanclub_id"]:
            return f"https://fantia.jp/fanclubs/{fanclub_id}"
        elif fanclub_name := url_properties["fanclub_name"]:
            return f"https://fantia.jp/{fanclub_name}"
        else:
            raise NotImplementedError

    @property
    def related(self) -> list[Url]:
        links = self.html.select_one(".fanclub-comment").parent.select("a")
        return [self.parse(link["href"]) for link in links]

    @property
    def primary_names(self) -> list[str]:
        nickname = self.html.select_one(".single-fanclub #nickname")["value"]
        assert nickname
        return [nickname]

    @property
    def secondary_names(self) -> list[str]:
        return []


class FantiaFanclubAssetUrl(GalleryAssetUrl, FantiaUrl):
    fanclub_id: int

    @property
    def full_size(self) -> str:
        return re.sub(r"(\d+\/)(\w+_)+", r"\1", self.parsed_url.raw_url).replace(".webp", ".jpg")


class FantiaImageUrl(PostAssetUrl, FantiaUrl):
    image_id: int
    image_type: str | None
    post_id: int | None
    image_uuid: str | None
    # could also be downloadable

    @property
    def full_size(self) -> str:
        if self.image_type == "post":
            assert self.post_id
            assert self.image_uuid
            return f"https://c.fantia.jp/uploads/post/file/{self.post_id}/{self.image_uuid}.{self.parsed_url.extension}"
        elif self.image_type == "product":
            assert self.post_id
            assert self.image_uuid
            return f"https://c.fantia.jp/uploads/product/image/{self.post_id}/{self.image_uuid}.{self.parsed_url.extension}"
        elif self.image_type == "product_image":
            assert self.image_uuid
            return f"https://c.fantia.jp/uploads/product_image/file/{self.image_id}/{self.image_uuid}.{self.parsed_url.extension}"
        else:
            return self.parsed_url.raw_url
            # FIXME: is it correct in case of https://fantia.jp/posts/343039/post_content_photo/1617547? Probably not. hmmm
