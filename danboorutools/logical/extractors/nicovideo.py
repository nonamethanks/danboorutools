from danboorutools.models.url import ArtistUrl, InfoUrl, PostUrl, RedirectUrl, Url


class NicovideoUrl(Url):
    pass


class NicovideoArtistUrl(ArtistUrl, NicovideoUrl):
    user_id: int


class NicovideoVideoUrl(PostUrl, NicovideoUrl):
    video_id: str


class NicovideoCommunityUrl(InfoUrl, NicovideoUrl):
    community_id: int


class NicovideoListUrl(RedirectUrl, NicovideoUrl):
    list_id: int


class NicovideoGameArtistUrl(ArtistUrl, NicovideoUrl):
    user_id: int
    # todo: related -> nicovideoartisturl
