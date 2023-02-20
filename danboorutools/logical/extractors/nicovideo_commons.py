from danboorutools.models.url import ArtistUrl, PostUrl, Url


class NicovideoCommonsUrl(Url):
    pass


class NicovideoCommonsArtistUrl(ArtistUrl, NicovideoCommonsUrl):
    user_id: int


class NicovideoCommonsPostUrl(PostUrl, NicovideoCommonsUrl):
    commons_id: str
