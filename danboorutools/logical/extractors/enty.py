from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class EntyUrl(Url):
    pass


class EntyPostUrl(PostUrl, EntyUrl):
    post_id: int

    normalize_string = "https://enty.jp/posts/{post_id}"


class EntyArtistUrl(ArtistUrl, EntyUrl):
    username: str | None
    user_id: int | None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        if username := kwargs["username"]:
            return f"https://enty.jp/{username}"
        elif user_id := kwargs["user_id"]:
            return f"https://enty.jp/users/{user_id}"
        else:
            raise ValueError


class EntyImageUrl(PostAssetUrl, EntyUrl):
    post_id: int


class EntyArtistImageUrl(GalleryAssetUrl, EntyUrl):
    user_id: int
