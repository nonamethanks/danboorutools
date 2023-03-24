from danboorutools.models.url import ArtistUrl, PostUrl, Url


class Nicovideo3dUrl(Url):
    pass


class Nicovideo3dPostUrl(PostUrl, Nicovideo3dUrl):
    post_id: int

    normalize_template = "https://3d.nicovideo.jp/works/td{post_id}"


class Nicovideo3dArtistUrl(ArtistUrl, Nicovideo3dUrl):
    username: str | None = None  # TODO: this is a redirect
    user_id: int | None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if user_id := kwargs.get("user_id"):
            return f"https://3d.nicovideo.jp/users/{user_id}"
        elif username := kwargs.get("username"):
            return f"https://3d.nicovideo.jp/u/{username}"
        else:
            raise NotImplementedError
