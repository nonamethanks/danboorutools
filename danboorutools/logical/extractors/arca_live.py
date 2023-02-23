from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class ArcaLiveUrl(Url):
    pass


class ArcaLivePostUrl(PostUrl, ArcaLiveUrl):
    post_id: int
    channel: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        channel = kwargs["channel"]
        post_id = kwargs["post_id"]
        return f"https://arca.live/b/{channel}/{post_id}"


class ArcaLiveArtistUrl(ArtistUrl, ArcaLiveUrl):
    user_id: int | None
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        username = kwargs["username"]
        if user_id := kwargs.get("user_id"):
            return f"https://arca.live/u/@{username}/{user_id}"
        else:
            return f"https://arca.live/u/@{username}"


class ArcaLiveImageUrl(PostAssetUrl, ArcaLiveUrl):
    date_string: str
    filename: str
