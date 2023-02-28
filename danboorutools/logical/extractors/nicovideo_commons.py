from danboorutools.models.url import ArtistUrl, PostUrl, Url


class NicovideoCommonsUrl(Url):
    pass


class NicovideoCommonsArtistUrl(ArtistUrl, NicovideoCommonsUrl):
    user_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://commons.nicovideo.jp/user/{kwargs['user_id']}"


class NicovideoCommonsPostUrl(PostUrl, NicovideoCommonsUrl):
    commons_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://commons.nicovideo.jp/material/{kwargs['commons_id']}"
