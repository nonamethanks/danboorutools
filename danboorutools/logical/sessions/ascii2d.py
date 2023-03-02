from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from ratelimit import limits, sleep_and_retry

from danboorutools.logical.extractors.pixiv import PixivArtistUrl
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

    @property
    def _url_groups(self) -> list[Tag]:
        url_groups = self.html_data.select(".detail-box h6")
        if not url_groups:
            raise NotImplementedError(self.html_data, self.search_url)
        return url_groups

    @cached_property
    def _data(self) -> dict[str, list]:
        data: dict[str, list] = {
            "primary_urls": [],
            "extra_urls": [],
            "primary_names": [],
            "secondary_names": [],
        }

        for url_group in self._url_groups:
            site = url_group.select_one("small").text.strip()

            if site == "pixiv":
                self.__parse_pixiv_result(url_group, data)
            elif site == "twitter":
                self.__parse_twitter_result(url_group, data)
            elif site == "dlsite":  # dlsite and dmm
                raise NotImplementedError(site, url_group)
                # for link in url_group.select("small a"):
                #     post_url = Url.parse(link["href"])

            else:
                raise NotImplementedError(site, url_group)

        return {key: list(dict.fromkeys(value)) for key, value in data.items()}

    @staticmethod
    def __parse_pixiv_result(url_group: Tag, data: dict[str, list]) -> None:
        post_url = Url.parse(url_group.select("a")[0]["href"])
        assert isinstance(post_url, PostUrl), post_url

        artist_element = url_group.select("a")[1]

        creator_url = Url.parse(artist_element["href"])
        assert isinstance(creator_url, InfoUrl), creator_url
        artist_name = artist_element.text

        assert isinstance(creator_url, PixivArtistUrl)
        data["primary_urls"].append(creator_url)
        data["primary_names"].append(artist_name)

    @staticmethod
    def __parse_twitter_result(url_group: Tag, data: dict[str, list]) -> None:
        post_url = Url.parse(url_group.select("a")[0]["href"])
        assert isinstance(post_url, PostUrl), post_url

        artist_element = url_group.select("a")[1]

        creator_url = Url.parse(artist_element["href"])
        assert isinstance(creator_url, InfoUrl), creator_url
        artist_name = artist_element.text

        assert isinstance(creator_url, TwitterIntentUrl)
        data["primary_urls"].append(Url.build(TwitterArtistUrl, username=artist_name))
        data["extra_urls"].append(creator_url)
        data["secondary_names"].append(artist_name)


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

        results = [
            Ascii2dArtistResult(result_html.select_one(".info-box"), ascii2d_url)
            for result_html in html_results
            if result_html.select_one(".detail-box").text.strip()  # some results have bare text that must be parsed
        ]

        assert results, url  # to make sure page layout hasn't changed
        return results

    def find_gallery(self, url: str, original_url: Url | str, original_post: DanbooruPost) -> Ascii2dArtistResult | None:
        for result in self._reverse_search_url(url):
            if result.md5 == original_post.md5:
                return result
            if Url.parse(original_url).normalized_url in [url.normalized_url for url in [result.primary_url] + result.extra_urls]:
                return result

            continue
        return None
