from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools.logical.extractors.dlsite import DlsiteWorkUrl
from danboorutools.logical.extractors.fanza import FanzaUrl
from danboorutools.logical.extractors.nicoseiga import NicoSeigaArtistUrl
from danboorutools.logical.extractors.nijie import NijieArtistUrl
from danboorutools.logical.extractors.pixiv import PixivArtistUrl
from danboorutools.logical.extractors.sakura import SakuraBlogUrl
from danboorutools.logical.extractors.tinami import TinamiArtistUrl
from danboorutools.logical.extractors.twitter import TwitterArtistUrl, TwitterIntentUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.url import InfoUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import memoize

if TYPE_CHECKING:
    from bs4 import Tag

    from danboorutools.models.danbooru import DanbooruPost


@dataclass(repr=False)
class Ascii2dArtistResult:
    html_data: Tag
    search_url: str

    def __repr__(self) -> str:
        stringified = ", ".join(f"{k}={v}" for k, v in self._data.items())
        return f"Ascii2dArtistResult({stringified} / {self.search_url})"

    @property
    def primary_url(self) -> InfoUrl:
        return self._data["primary_urls"][0]

    @property
    def extra_urls(self) -> list[InfoUrl]:
        return self._data["primary_urls"][1:] + self._data["extra_urls"]

    @property
    def posts(self) -> list[PostUrl]:
        return self._data["posts"]

    @property
    def primary_names(self) -> list[str]:
        return self._data["primary_names"]

    @property
    def secondary_names(self) -> list[str]:
        return self._data["secondary_names"]

    @property
    def md5(self) -> str:
        return self.html_data.select_one(".hash").text

    @cached_property
    def _data(self) -> dict[str, list]:
        data: dict[str, list] = {
            "primary_urls": [],
            "extra_urls": [],
            "primary_names": [],
            "secondary_names": [],
            "posts": [],
        }

        if url_groups := self.html_data.select(".detail-box h6"):
            self.__detail_box_h6_case(url_groups, data)
        elif url_groups := self.html_data.select(".detail-box a"):
            self.__detail_box_a_case(url_groups, data)
        elif url_groups := self.html_data.select(".external"):
            self.__external_case(url_groups, data)
        else:
            raise NotImplementedError(self.html_data, self.search_url)

        return {key: list(dict.fromkeys(value)) for key, value in data.items()}

    def __detail_box_h6_case(self, url_groups: list[Tag], data: dict[str, list]) -> None:
        for link_object in url_groups:
            site = link_object.select_one("small").text.strip()

            post_url = Url.parse(link_object.select("a")[0]["href"])
            assert isinstance(post_url, PostUrl), post_url
            data["posts"].append(post_url)
            try:
                artist_element = link_object.select("a")[1]
            except IndexError as e:
                if isinstance(post_url, FanzaUrl):
                    data["primary_urls"].append(post_url.artist)
                    continue
                e.add_note(str(link_object))
                raise
            creator_url = Url.parse(artist_element["href"])
            assert isinstance(creator_url, InfoUrl), creator_url
            artist_name = artist_element.text

            if site == "pixiv":
                self.__parse_pixiv_result(creator_url, artist_name, data)
            elif site == "twitter":
                self.__parse_twitter_result(creator_url, artist_name, data)
            elif site == "ニコニコ静画":
                self.__parse_seiga_result(creator_url, artist_name, data)
            elif site == "tinami":
                self.__parse_tinami_result(creator_url, artist_name, data)
            elif site == "ニジエ":
                self.__parse_nijie_result(creator_url, artist_name, data)
            else:
                raise NotImplementedError(site, artist_element, self.search_url)

    def __detail_box_a_case(self, url_groups: list[Tag], data: dict[str, list]) -> None:
        for link_object in url_groups:
            site = link_object.text.strip()
            if site == "dlsite":
                self.__parse_dlsite_result(link_object, data)
            else:
                raise NotImplementedError(site, link_object, self.search_url)

    def __external_case(self, url_groups: list[Tag], data: dict[str, list]) -> None:
        if not url_groups:
            raise NotImplementedError(self.html_data, self.search_url)

        if len(url_groups) > 1:
            raise NotImplementedError(url_groups, self.search_url)

        if "sakura.ne.jp" in url_groups[0].text:
            self.__parse_sakura_result(url_groups[0], data)
        elif "DL版" in url_groups[0].text:
            return
        else:
            raise NotImplementedError(url_groups, self.search_url)

    @staticmethod
    def __parse_pixiv_result(creator_url: InfoUrl, artist_name: str, data: dict[str, list]) -> None:
        assert isinstance(creator_url, PixivArtistUrl)
        data["primary_urls"].append(creator_url)
        data["primary_names"].append(artist_name)

    @staticmethod
    def __parse_twitter_result(creator_url: InfoUrl, artist_name: str, data: dict[str, list]) -> None:
        assert isinstance(creator_url, TwitterIntentUrl)
        data["primary_urls"].append(Url.build(TwitterArtistUrl, username=artist_name))
        data["extra_urls"].append(creator_url)
        data["secondary_names"].append(artist_name)

    @staticmethod
    def __parse_seiga_result(creator_url: InfoUrl, artist_name: str, data: dict[str, list]) -> None:
        assert isinstance(creator_url, NicoSeigaArtistUrl)
        data["primary_urls"].append(creator_url)
        data["primary_names"].append(artist_name)

    @staticmethod
    def __parse_tinami_result(creator_url: InfoUrl, artist_name: str, data: dict[str, list]) -> None:
        assert isinstance(creator_url, TinamiArtistUrl)
        data["primary_urls"].append(creator_url)
        data["primary_names"].append(artist_name)

    @staticmethod
    def __parse_nijie_result(creator_url: InfoUrl, artist_name: str, data: dict[str, list]) -> None:
        assert isinstance(creator_url, NijieArtistUrl)
        data["primary_urls"].append(creator_url)
        data["primary_names"].append(artist_name)

    @staticmethod
    def __parse_dlsite_result(url_element: Tag, data: dict[str, list]) -> None:
        url = url_element["href"]
        book = Url.parse(url)
        assert isinstance(book, DlsiteWorkUrl)
        data["posts"].append(book)
        data["primary_urls"].append(book.gallery)

    @staticmethod
    def __parse_sakura_result(element: Tag, data: dict[str, list]) -> None:
        name, url = element.text.split("'")
        sakura_url = Url.parse(url)
        assert isinstance(sakura_url, SakuraBlogUrl)
        data["primary_names"].append(name)
        data["primary_urls"].append(sakura_url)


class Ascii2dSession(Session):
    MAX_CALLS_PER_SECOND = 0.5

    @memoize
    def _reverse_search_url(self, url: str) -> list[Ascii2dArtistResult]:
        # can't use /color/md5 because sometimes the result is not cached and requires a cloudflare-protected POST
        ascii2d_url = f"https://ascii2d.net/search/url/{url}"
        response = self.get_html(ascii2d_url)

        html_results = response.select(".item-box")
        assert html_results, url

        results: list[Ascii2dArtistResult] = []
        for result_html in html_results:
            if result_html.select_one(".detail-box").text.strip():
                result = Ascii2dArtistResult(result_html.select_one(".info-box"), ascii2d_url)
                if not any(v for v in result._data.values()):
                    continue
                results.append(result)

        assert results, f"No parsable results for {url}"  # to make sure page layout hasn't changed
        return results

    def find_gallery(self, url: str, original_url: Url | str, original_post: DanbooruPost) -> Ascii2dArtistResult | None:
        for result in self._reverse_search_url(url):
            if result.md5 == original_post.md5:
                return result

            original_url = Url.parse(original_url)
            if isinstance(original_url, PostAssetUrl):
                original_url = original_url.post

            normalized_from_result = [url.normalized_url for url in [result.primary_url, *result.extra_urls, *result.posts]]
            if original_url.normalized_url in normalized_from_result:
                return result

            continue
        return None
