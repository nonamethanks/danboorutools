from __future__ import annotations

from functools import cached_property
from typing import Literal
from urllib.parse import urljoin

from danboorutools.logical.sessions.fanza import FanzaBookData, FanzaSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class FanzaUrl(Url):
    session = FanzaSession()


class FanzaDoujinWorkUrl(PostUrl, FanzaUrl):
    work_id: str
    subsubsite: Literal["dc", "digital", "mono"]

    normalize_template = "https://www.dmm.co.jp/{subsubsite}/doujin/-/detail/=/cid={work_id}/"

    @cached_property
    def gallery(self) -> FanzaDoujinAuthorUrl:
        if self.subsubsite == "dc":
            url = self.html.select_one(".circleName__txt")["href"]
        else:
            raise NotImplementedError(self)

        parsed = Url.parse(urljoin("https://www.dmm.co.jp/", url))
        assert isinstance(parsed, FanzaDoujinAuthorUrl), (self, parsed)
        return parsed


class FanzaDoujinAuthorUrl(ArtistUrl, FanzaUrl):
    user_id: int
    subsubsite: str

    # article=maker -> circle. gotta be careful to extract the correct author
    normalize_template = "https://www.dmm.co.jp/{subsubsite}/doujin/-/list/=/article=maker/id={user_id}/"

    @property
    def related(self) -> list[Url]:
        return []

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return []


class FanzaDlsoftWorkUrl(PostUrl, FanzaUrl):
    work_id: str
    subsubsite: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if kwargs["subsubsite"] == "mono":
            return f"https://www.dmm.co.jp/mono/pcgame/-/detail/=/cid={kwargs['work_id']}/"
        else:
            return f"https://dlsoft.dmm.co.jp/detail/{kwargs['work_id']}/"

    @property
    def gallery(self) -> FanzaDlsoftAuthorUrl:
        artists = self.html.select_one(".main-area-center").find("td", string="原画").parent.select("td.type-right a")
        if len(artists) != 1:
            raise NotImplementedError("Found more than one artist:", self, artists)

        parsed = Url.parse(artists[0]["href"])
        assert isinstance(parsed, FanzaDlsoftAuthorUrl)
        return parsed


class FanzaDlsoftAuthorUrl(ArtistUrl, FanzaUrl):
    user_id: int
    user_type: Literal["article=maker", "article=author"] = "article=maker"

    normalize_template = "https://dlsoft.dmm.co.jp/list/{user_type}/id={user_id}/"  # circle or author


class FanzaGamesGameUrl(PostUrl, FanzaUrl):
    game_name: str

    normalize_template = "https://games.dmm.co.jp/detail/{game_name}"


class FanzaGamesOldGameUrl(RedirectUrl, FanzaUrl):
    game_id: int

    normalize_template = "http://sp.dmm.co.jp/netgame/application/detail/app_id/{game_id}"


class FanzaBookWorkUrl(PostUrl, FanzaUrl):
    series_id: int | None
    work_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if series_id := kwargs.get("series_id"):
            return f"https://book.dmm.co.jp/product/{series_id}/{kwargs['work_id']}/"
        else:
            return f"https://www.dmm.co.jp/mono/book/-/detail/=/cid={kwargs['work_id']}/"
        # different from FanzaBookNoSeriesUrl, in that "mono" books do not redirect because they're region-restricted
        # what a clusterfuck!

    @property
    def book_data(self) -> FanzaBookData:
        return self.session.book_data(self.work_id)

    @property
    def gallery(self) -> FanzaBookAuthorUrl:
        if len(self.book_data.author) != 1:
            raise NotImplementedError(self, self.book_data.author)
        author_id = self.book_data.author[0]["id"]
        return FanzaBookAuthorUrl.build(user_id=int(author_id))


class FanzaBookNoSeriesUrl(RedirectUrl, FanzaUrl):
    work_id: str

    normalize_template = "https://book.dmm.co.jp/detail/{work_id}/"


class FanzaBookAuthorUrl(ArtistUrl, FanzaUrl):
    user_id: int

    normalize_template = "https://book.dmm.co.jp/list/?author={user_id}"


class FanzaImageUrl(PostAssetUrl, FanzaUrl):
    work_type: Literal["doujin", "dlsoft", "book", "freegame", "netgame", "good", "video"]
    work_id: str
    page: int

    @property
    def full_size(self) -> str:
        if self.work_type == "netgame":
            return self.parsed_url.raw_url

        base_path = f"https://{self.parsed_url.hostname}/{self.parsed_url.url_parts[0]}/{self.parsed_url.url_parts[1]}"

        if self.page == 0:
            return f"{base_path}/{self.work_id}/{self.work_id}pl.jpg"
        elif self.work_type == "freegame":
            return f"{base_path}/{self.work_id}/{self.work_id}jp-{self.page:02d}.jpg"
        else:
            return f"{base_path}/{self.work_id}/{self.work_id}jp-{self.page:03d}.jpg"
