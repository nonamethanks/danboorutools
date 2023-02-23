from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PatreonUrl(Url):
    pass


class PatreonPostUrl(PostUrl, PatreonUrl):
    post_id: int
    title: str | None = None
    username: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        title = kwargs.get("title")
        post_id = kwargs["post_id"]
        if title:
            return f"https://www.patreon.com/posts/{title}-{post_id}"
        else:
            return f"https://www.patreon.com/posts/{post_id}"


class PatreonArtistUrl(ArtistUrl, PatreonUrl):
    user_id: int | None = None
    username: str | None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        user_id = kwargs.get("user_id")
        username = kwargs.get("username")
        if username:
            return f"http://www.patreon.com/{username}"
        elif user_id:
            return f"https://www.patreon.com/user?u={user_id}"
        else:
            raise NotImplementedError


class PatreonImageUrl(PostAssetUrl, PatreonUrl):
    post_id: int | None = None
