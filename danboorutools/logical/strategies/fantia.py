from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class FantiaUrl(Url):
    pass


class FantiaPostUrl(PostUrl, FantiaUrl):
    normalization = "https://fantia.jp/{post_type}s/{post_id}"

    post_id: int
    post_type: str


class FantiaFanclubUrl(ArtistUrl, FantiaUrl):
    fanclub_id: int | None
    fanclub_name: str | None

    @classmethod
    def _normalize_from_properties(cls, **url_properties) -> str:
        fanclub_id: int | None = url_properties["user_id"]
        fanclub_name: str | None = url_properties["username"]

        if fanclub_id:
            return f"https://fantia.jp/fanclubs/{fanclub_id}"
        else:
            assert fanclub_name
            return f"https://fantia.jp/{fanclub_name}"


class FantiaFanclubAssetUrl(GalleryAssetUrl, FantiaUrl):
    fanclub_id: int


class FantiaImageUrl(PostAssetUrl, FantiaUrl):
    image_id: int
    image_type: str | None
    post_id: int | None
    # could also be downloadable
