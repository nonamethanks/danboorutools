import re
from functools import cached_property

from danboorutools.logical.sessions.mixi import MixiSession
from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, DeadDomainUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class MixiUrl(Url):
    session = MixiSession()


class MixiProfileUrl(ArtistUrl, MixiUrl):
    profile_id: int

    normalize_template = "https://mixi.jp/show_friend.pl?id={profile_id}"

    @property
    def primary_names(self) -> list[str]:
        name_el = self.html.select_one(".profilePhoto a.name")
        assert name_el, self
        name_match = re.match(r"^(.*)さん\(\d+\)$", name_el.text.strip())
        assert name_match, name_el.text.strip()
        return [name_match.groups()[0]]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        profile_el = self.html.select_one("#profile .sectionBody")
        assert profile_el, self
        return list(map(Url.parse, extract_urls_from_string(profile_el.text)))


class MixiImageUrl(PostAssetUrl, MixiUrl):
    ...


class MixiVideoUrl(DeadDomainUrl, PostUrl, MixiUrl):
    video_id: int

    normalize_template = "https://video.mixi.jp/list_video.pl?id={video_id}"


class MixiPageUrl(DeadDomainUrl, PostUrl, MixiUrl):
    page_id: int

    normalize_template = "https://page.mixi.jp/view_page.pl?page_id={page_id}"


class MixiCommunityUrl(ArtistAlbumUrl, MixiUrl):
    community_id: int

    normalize_template = "https://mixi.jp/view_community.pl?id={community_id}"


class MixiCommunityPostUrl(PostUrl, MixiUrl):
    community_id: int
    post_id: int

    normalize_template = "https://mixi.jp/view_bbs.pl?id={post_id}&comm_id={community_id}"


class MixiAlbumUrl(ArtistAlbumUrl, MixiUrl):
    album_id: int
    owner_id: int

    normalize_template = "https://photo.mixi.jp/view_album.pl?album_id={album_id}&owner_id={owner_id}"

    @cached_property
    def gallery(self) -> MixiProfileUrl:
        return MixiProfileUrl.build(profile_id=self.owner_id)


class MixiPhotoUrl(PostUrl, MixiUrl):
    owner_id: int
    photo_id: int

    normalize_template = "https://photo.mixi.jp/view_photo.pl?photo_id={photo_id}&owner_id={owner_id}"

    @cached_property
    def gallery(self) -> MixiProfileUrl:
        return MixiProfileUrl.build(profile_id=self.owner_id)


class MixiApplicationUrl(PostUrl, MixiUrl):
    owner_id: int
    application_id: int

    normalize_template = "https://mixi.jp/run_appli.pl?id={application_id}&owner_id={owner_id}"

    @cached_property
    def gallery(self) -> MixiProfileUrl:
        return MixiProfileUrl.build(profile_id=self.owner_id)


class MixiDiaryUrl(PostUrl, MixiUrl):
    owner_id: int
    diary_id: int

    normalize_template = "https://mixi.jp/view_diary.pl?id={diary_id}&owner_id={owner_id}"

    @cached_property
    def gallery(self) -> MixiProfileUrl:
        return MixiProfileUrl.build(profile_id=self.owner_id)
