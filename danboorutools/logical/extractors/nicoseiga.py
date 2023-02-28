from typing import Literal

from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class NicoSeigaUrl(Url):
    pass


class NicoSeigaIllustUrl(PostUrl, NicoSeigaUrl):
    illust_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://seiga.nicovideo.jp/seiga/im{kwargs['illust_id']}"


class NicoSeigaMangaUrl(PostUrl, NicoSeigaUrl):
    manga_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://seiga.nicovideo.jp/watch/mg{kwargs['manga_id']}"


class NicoSeigaComicUrl(ArtistAlbumUrl, NicoSeigaUrl):
    comic_id: int | str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://seiga.nicovideo.jp/comic/{kwargs['comic_id']}"


class NicoSeigaArtistUrl(ArtistUrl, NicoSeigaUrl):
    user_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://seiga.nicovideo.jp/user/illust/{kwargs['user_id']}"


class NicoSeigaImageUrl(PostAssetUrl, NicoSeigaUrl):
    image_id: int
    image_type: Literal["manga", "illust"] | None
    # TODO: when getting full filename, compare timestamp and dont recompute if it's still viable

    @property
    def full_size(self) -> str:
        return f"https://seiga.nicovideo.jp/image/source/{self.image_id}"
