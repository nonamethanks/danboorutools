from danboorutools.models.url import ArtistUrl, InfoUrl, PostUrl, RedirectUrl, Url


class NicovideoUrl(Url):
    pass


class NicovideoArtistUrl(ArtistUrl, NicovideoUrl):
    user_id: int

    normalize_string = "https://www.nicovideo.jp/user/{user_id}"


class NicovideoVideoUrl(PostUrl, NicovideoUrl):
    video_id: str

    normalize_string = "https://www.nicovideo.jp/watch/{video_id}"


class NicovideoCommunityUrl(InfoUrl, NicovideoUrl):
    community_id: int

    normalize_string = "https://com.nicovideo.jp/community/co{community_id}"


class NicovideoListUrl(RedirectUrl, NicovideoUrl):
    list_id: int

    normalize_string = "http://www.nicovideo.jp/mylist/{list_id}"


class NicovideoGameArtistUrl(ArtistUrl, NicovideoUrl):
    user_id: int

    normalize_string = "https://game.nicovideo.jp/atsumaru/users/{user_id}"

    # todo: related -> nicovideoartisturl
