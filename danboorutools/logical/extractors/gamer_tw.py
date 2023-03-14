from typing import Literal

from danboorutools.models.url import ArtistUrl, PostUrl, Url


class GamerTwUrl(Url):
    pass


class GamerTwArtistUrl(ArtistUrl, GamerTwUrl):
    artist_id: str

    normalize_template = "https://home.gamer.com.tw/homeindex.php?owner={artist_id}"

    @property
    def is_deleted(self) -> bool:
        if "查詢失敗" in str(self.html):
            return True
        elif self.html.select_one("#BH-master"):
            return False
        else:
            raise NotImplementedError(self)

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.artist_id]

    @property
    def related(self) -> list[Url]:
        return []


class GamerTwPostUrl(PostUrl, GamerTwUrl):
    post_id: int

    normalize_template = "https://home.gamer.com.tw/creationDetail.php?sn={post_id}"

    @property
    def is_deleted(self) -> bool:
        if "查無此作品" in str(self.html):
            return True
        elif self.html.select_one(".creation-container"):
            return False
        else:
            raise NotImplementedError(self)


class GamerTwForumPostUrl(PostUrl, GamerTwUrl):
    subforum: str
    bsn: int
    sn: int
    sn_type: Literal["sn", "snA"]

    normalize_template = "https://forum.gamer.com.tw/{subforum}?bsn={bsn}&{sn_type}={sn}"


class GamerTwGnnPostUrl(PostUrl, GamerTwUrl):
    post_id: int

    normalize_template = "https://gnn.gamer.com.tw/detail.php?sn={post_id}"
