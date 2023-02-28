from danboorutools.models.url import ArtistUrl, InfoUrl, PostUrl, RedirectUrl, Url


class NicovideoUrl(Url):
    pass


class NicovideoArtistUrl(ArtistUrl, NicovideoUrl):
    user_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.nicovideo.jp/user/{kwargs['user_id']}"


class NicovideoVideoUrl(PostUrl, NicovideoUrl):
    video_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.nicovideo.jp/watch/{kwargs['video_id']}"


class NicovideoCommunityUrl(InfoUrl, NicovideoUrl):
    community_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://com.nicovideo.jp/community/co{kwargs['community_id']}"


class NicovideoListUrl(RedirectUrl, NicovideoUrl):
    list_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"http://www.nicovideo.jp/mylist/{kwargs['list_id']}"


class NicovideoGameArtistUrl(ArtistUrl, NicovideoUrl):
    user_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://game.nicovideo.jp/atsumaru/users/{kwargs['user_id']}"

    # todo: related -> nicovideoartisturl
