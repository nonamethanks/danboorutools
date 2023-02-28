from danboorutools.models.url import ArtistUrl, PostUrl, Url


class NicovideoCommonsUrl(Url):
    pass


class NicovideoCommonsArtistUrl(ArtistUrl, NicovideoCommonsUrl):
    user_id: int

    normalize_string = "https://commons.nicovideo.jp/user/{user_id}"


class NicovideoCommonsPostUrl(PostUrl, NicovideoCommonsUrl):
    commons_id: str

    normalize_string = "https://commons.nicovideo.jp/material/{commons_id}"
