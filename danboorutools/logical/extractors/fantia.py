import re

from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class FantiaUrl(Url):
    pass


class FantiaPostUrl(PostUrl, FantiaUrl):
    post_id: int
    post_type: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        post_type = kwargs["post_type"]
        return f"https://fantia.jp/{post_type}/{post_id}"


class FantiaFanclubUrl(ArtistUrl, FantiaUrl):
    fanclub_id: int | None
    fanclub_name: str | None

    @classmethod
    def normalize(cls, **url_properties) -> str:
        fanclub_id: int | None = url_properties["fanclub_id"]
        fanclub_name: str | None = url_properties["fanclub_name"]

        if fanclub_id:
            return f"https://fantia.jp/fanclubs/{fanclub_id}"
        elif fanclub_name:
            return f"https://fantia.jp/{fanclub_name}"
        else:
            raise NotImplementedError


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
