from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from ratelimit import limits, sleep_and_retry

from danboorutools.logical.extractors.dlsite import DlsiteWorkUrl
from danboorutools.logical.extractors.pixiv import PixivArtistUrl
from danboorutools.logical.extractors.sakura import SakuraBlogUrl
from danboorutools.logical.extractors.twitter import TwitterArtistUrl, TwitterIntentUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.danbooru import DanbooruPost
from danboorutools.models.url import InfoUrl, PostUrl, Url
from danboorutools.util.misc import memoize

if TYPE_CHECKING:
    from bs4 import Tag


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
    def primary_names(self) -> list[str]:
        return self._data["primary_names"]

    @property
    def secondary_names(self) -> list[str]:
        return self._data["secondary_names"]

    @property
    def md5(self) -> str:
        return self.html_data.select_one(".hash").text

    @cached_property
    def _data(self) -> dict[str, list]:  # pylint: disable=too-many-branches # can't be helped
        data: dict[str, list] = {
            "primary_urls": [],
            "extra_urls": [],
            "primary_names": [],
            "secondary_names": [],
        }

        if url_groups := self.html_data.select(".detail-box h6"):
            for link_object in url_groups:
                site = link_object.select_one("small").text.strip()

                post_url = Url.parse(link_object.select("a")[0]["href"])
                assert isinstance(post_url, PostUrl), post_url

                artist_element = link_object.select("a")[1]

                if site == "pixiv":
                    self.__parse_pixiv_result(artist_element, data)
                elif site == "twitter":
                    self.__parse_twitter_result(artist_element, data)
                else:
                    raise NotImplementedError(site, artist_element)
        elif url_groups := self.html_data.select(".detail-box a"):
            for link_object in url_groups:
                site = link_object.text.strip()
                if site == "dlsite":
                    self.__parse_dlsite_result(link_object, data)
                else:
                    raise NotImplementedError(site, link_object)
        elif url_groups := self.html_data.select(".external"):
            if len(url_groups) > 1:
                raise NotImplementedError(self.html_data, self.search_url)
            if "sakura.ne.jp" in url_groups[0].text:
                self.__parse_sakura_result(url_groups[0], data)
            else:
                raise NotImplementedError(self.html_data, self.search_url)
        else:
            raise NotImplementedError(self.html_data, self.search_url)

        return {key: list(dict.fromkeys(value)) for key, value in data.items()}

    @staticmethod
    def __parse_sakura_result(element: Tag, data: dict[str, list]) -> None:
        print(str(element), str(element).split("<br>"))
        name, url = str(element).split("<br>")
        sakura_url = Url.parse(url)
        assert isinstance(sakura_url, SakuraBlogUrl)
        data["primary_names"].append(name)
        data["primary_urls"].append(sakura_url)

    @staticmethod
    def __parse_pixiv_result(artist_element: Tag, data: dict[str, list]) -> None:
        creator_url = Url.parse(artist_element["href"])
        assert isinstance(creator_url, InfoUrl), creator_url
        artist_name = artist_element.text

        assert isinstance(creator_url, PixivArtistUrl)
        data["primary_urls"].append(creator_url)
        data["primary_names"].append(artist_name)

    @staticmethod
    def __parse_twitter_result(artist_element: Tag, data: dict[str, list]) -> None:
        creator_url = Url.parse(artist_element["href"])
        assert isinstance(creator_url, InfoUrl), creator_url
        artist_name = artist_element.text

        assert isinstance(creator_url, TwitterIntentUrl)
        data["primary_urls"].append(Url.build(TwitterArtistUrl, username=artist_name))
        data["extra_urls"].append(creator_url)
        data["secondary_names"].append(artist_name)

    @staticmethod
    def __parse_dlsite_result(url_element: Tag, data: dict[str, list]) -> None:
        print(url_element)
        url = url_element["href"]
        book = Url.parse(url)
        assert isinstance(book, DlsiteWorkUrl)
        data["primary_urls"].append(book.gallery)


class Ascii2dSession(Session):
    @memoize
    @sleep_and_retry
    @limits(calls=1, period=2)
    def _reverse_search_url(self, url: str) -> list[Ascii2dArtistResult]:
        # can't use /color/md5 because sometimes the result is not cached and requires a cloudflare-protected POST
        ascii2d_url = f"https://ascii2d.net/search/url/{url}"
        response = self.get_html(ascii2d_url)

        html_results = response.select(".item-box")
        assert html_results, url

        results: list[Ascii2dArtistResult] = []
        for result_html in html_results:
            if result_html.select_one(".detail-box").text.strip():  # some results have bare text that must be parsed
                result = Ascii2dArtistResult(result_html.select_one(".info-box"), ascii2d_url)
                if not any(v for v in result._data.values()):  # ensure every result has some data in it
                    raise NotImplementedError(result_html, f"This result could not be parsed, found in {ascii2d_url}")
                results.append(result)

        assert results, f"No parsable results for {url}"  # to make sure page layout hasn't changed
        return results

    def find_gallery(self, url: str, original_url: Url | str, original_post: DanbooruPost) -> Ascii2dArtistResult | None:
        for result in self._reverse_search_url(url):
            if result.md5 == original_post.md5:
                return result
            if Url.parse(original_url).normalized_url in [url.normalized_url for url in [result.primary_url] + result.extra_urls]:
                return result

            continue
        return None
