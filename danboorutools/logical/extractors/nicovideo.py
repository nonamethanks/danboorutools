from danboorutools.exceptions import HTTPError
from danboorutools.models.url import ArtistUrl, InfoUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import settable_property


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

    @property
    def private(self) -> bool:
        try:
            self.html
        except HTTPError as e:
            if e.response is not None:
                return "このコミュニティのフォロワーではありません" in e.response.text
            raise
        else:
            return False

    @property
    def related(self) -> list[Url]:
        if self.private:
            return []  # don't bother
        raise NotImplementedError(self)  # extract nicovideo.jp, seiga here

    @property
    def primary_names(self) -> list[str]:
        if self.private:
            return []  # don't bother
        raise NotImplementedError(self)

    @property
    def secondary_names(self) -> list[str]:
        if self.private:
            return []  # don't bother
        raise NotImplementedError(self)

    @settable_property
    def is_deleted(self) -> bool:
        if self.private:
            return False
        if self.html.select_one(".communityInfo .communityData .title"):
            return False
        if "お探しのコミュニティは存在しないか、削除された可能性があります" in self.html:
            return True
        raise NotImplementedError(self)


class NicovideoListUrl(RedirectUrl, NicovideoUrl):
    list_id: int

    normalize_string = "http://www.nicovideo.jp/mylist/{list_id}"


class NicovideoGameArtistUrl(ArtistUrl, NicovideoUrl):
    user_id: int

    normalize_string = "https://game.nicovideo.jp/atsumaru/users/{user_id}"

    # todo: related -> nicovideoartisturl
