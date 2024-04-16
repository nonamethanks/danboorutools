import re
from functools import cached_property
from typing import Literal

from danboorutools.logical.sessions.dlsite import DlsiteSession
from danboorutools.logical.urls.dlsite_cien import DlsiteCienCreatorUrl
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class DlsiteUrl(Url):
    subsite: Literal[
        "books",                    # Adult Manga
        "home",                     # Safe Doujinshi
        "maniax", "girls", "bl",    # Adult Doujinshi
        "doujin",                   # Doujinshi images, redirects to the above ones
        "pro",                      # H Games
    ]

    session = DlsiteSession()


class DlsiteAuthorUrl(ArtistUrl, DlsiteUrl):
    author_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if (subsite := kwargs["subsite"]) in ["maniax", "girls", "bl", "home", "pro"]:
            return f"https://www.dlsite.com/{subsite}/circle/profile/=/maker_id/{kwargs["author_id"]}"
        elif subsite == "books":
            return f"https://www.dlsite.com/books/author/=/author_id/{kwargs["author_id"]}"
        else:
            raise NotImplementedError(subsite)

    @property
    def related(self) -> list[Url]:
        cien_id = self.session.cien_id_from_circle_id(self.author_id)
        return [DlsiteCienCreatorUrl.build(creator_id=cien_id)]

    @property
    def primary_names(self) -> list[str]:
        # this is in 99% of cases the circle's name, so it's not worth it
        return []

    @property
    def secondary_names(self) -> list[str]:
        return []


class DlsiteWorkUrl(PostUrl, DlsiteUrl):
    work_id: str
    status: Literal["work", "announce"]

    normalize_template = "https://www.dlsite.com/{subsite}/{status}/=/product_id/{work_id}"

    @cached_property
    def gallery(self) -> DlsiteAuthorUrl:
        maker_details = self.html.select_one("#work_maker")
        artist_url = DlsiteAuthorUrl.parse_and_assert(maker_details.select_one("a").attrs["href"])
        return artist_url


class DlsiteImageUrl(PostAssetUrl, DlsiteUrl):
    work_id: str
    status: Literal["work", "ana"]

    @property
    def full_size(self) -> str:
        url = self.parsed_url.raw_url.replace("/resize/", "/modpub/")
        url = re.sub(r"_\d+x\d+\.(\w+)", r".\1", url).replace(".webp", ".jpg")
        return url


class DlsiteKeywordSearch(RedirectUrl, DlsiteUrl):
    keyword: str
    normalize_template = 'https://www.dlsite.com/{subsite}/fsr/=/keyword_creater/"{keyword}"'

    @cached_property
    def resolved(self) -> Url:
        raise NotImplementedError  # need to extract from the html (no need to fetch a post)
