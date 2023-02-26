from danboorutools.models.url import ArtistUrl, PostUrl, Url


class InstagramUrl(Url):
    pass


class InstagramPostUrl(PostUrl, InstagramUrl):
    post_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.instagram.com/p/{kwargs['post_id']}"


class InstagramArtistUrl(ArtistUrl, InstagramUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.instagram.com/{kwargs['username']}"
