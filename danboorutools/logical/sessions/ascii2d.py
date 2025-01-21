from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools import logger
from danboorutools.exceptions import DeadUrlError, HTTPError
from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.amazon import AmazonItemUrl
from danboorutools.logical.urls.dlsite import DlsiteUrl, DlsiteWorkUrl
from danboorutools.logical.urls.fanbox import FanboxArtistUrl
from danboorutools.logical.urls.fantia import FantiaFanclubUrl
from danboorutools.logical.urls.fanza import FanzaDoujinWorkUrl, FanzaUrl
from danboorutools.logical.urls.lofter import LofterPostUrl
from danboorutools.logical.urls.melonbooks import MelonbooksProductUrl
from danboorutools.logical.urls.nicoseiga import NicoSeigaArtistUrl, NicoSeigaIllustUrl
from danboorutools.logical.urls.nijie import NijieArtistUrl
from danboorutools.logical.urls.pixiv import PixivArtistUrl, PixivPostUrl
from danboorutools.logical.urls.sakura import SakuraBlogUrl
from danboorutools.logical.urls.tinami import TinamiArtistUrl
from danboorutools.logical.urls.twitter import TwitterArtistUrl, TwitterIntentUrl, TwitterPostUrl
from danboorutools.models.url import InfoUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string

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

    def __bool__(self):
        return any(v for v in self._data.values())

    @property
    def found_urls(self) -> list[InfoUrl]:
        return self._data["found_urls"]

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
            "found_urls": [],
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
            if link_object.text == "2ちゃんねるのログ":
                continue

            site_el = link_object.select_one("small")
            if not site_el:
                if link_object.text.strip() == "麻生 FANBOX":
                    continue

                raise ValueError(link_object)

            site = site_el.text.strip()
            if site in ["dlsite", "dmm", "amazon"]:
                for sublink in link_object.select("a"):
                    work_url = Url.parse(sublink["href"])
                    assert isinstance(work_url, FanzaUrl | DlsiteUrl | AmazonItemUrl), work_url
                    assert isinstance(work_url, PostUrl), work_url
                    # try:
                    #     data["found_urls"].append(work_url.artist)
                    # except NotImplementedError as e:
                    #     if "Found more than one artist:" in str(e):  # not worth it
                    #         continue
                    #     raise
                continue

            first_url = PostUrl.parse_and_assert(link_object.select("a")[0]["href"])
            data["posts"].append(first_url)
            # try:
            artist_element = link_object.select("a")[1]
            # except IndexError as e:
            #    if isinstance(post_url, (FanzaUrl, DlsiteUrl)):
            #        data["found_urls"].append(post_url.artist)
            #        continue
            #    e.add_note(f"{link_object} {post_url}")
            #    raise
            second_url = Url.parse(artist_element["href"])
            if isinstance(second_url, MelonbooksProductUrl):
                data["posts"].append(second_url)
                data["found_urls"] += [u.gallery for u in data["posts"]]
                continue

            assert isinstance(second_url, InfoUrl), second_url
            artist_name = artist_element.text

            data["found_urls"].append(second_url)
            if site in ["pixiv", "fanbox", "ニジエ", "tinami", "ニコニコ静画", "fantia"]:
                assert isinstance(
                    second_url,
                    PixivArtistUrl | FanboxArtistUrl | NijieArtistUrl | TinamiArtistUrl | NicoSeigaArtistUrl | FantiaFanclubUrl,
                )
                data["primary_names"].append(artist_name)
            elif site == "twitter":
                assert isinstance(second_url, TwitterIntentUrl)
                data["found_urls"].append(TwitterArtistUrl.build(username=artist_name))
                data["secondary_names"].append(artist_name)
            else:
                raise NotImplementedError(site, artist_element, self.search_url)

    def __detail_box_a_case(self, url_groups: list[Tag], data: dict[str, list]) -> None:
        for link_object in url_groups:
            site = link_object.text.strip()
            if site == "dlsite":
                self.__parse_dlsite_result(link_object, data)
            elif site == "dmm":
                self.__parse_fanza_result(link_object, data)
            elif link_object.has_attr("href"):
                post_url = Url.parse(url_groups[0].attrs["href"])
                try:
                    artist_url = Url.parse(url_groups[1].attrs["href"])
                except IndexError:
                    artist_url = None
                else:
                    artist_name = url_groups[1].text

                if artist_url:
                    data["found_urls"].append(artist_url)
                if isinstance(post_url, PixivPostUrl) and isinstance(artist_url, PixivArtistUrl):
                    data["primary_names"].append(artist_name)
                    data["posts"].append(post_url)
                elif isinstance(post_url, TwitterPostUrl) and isinstance(artist_url, TwitterArtistUrl):
                    data["secondary_names"].append(artist_name)
                elif isinstance(post_url, DlsiteWorkUrl | FanzaDoujinWorkUrl) and artist_url is None:
                    # https://ascii2d.net/search/color/82e1cf49e0418979f5a69cd279cd9948
                    # https://ascii2d.net/search/color/497ca528f56464ce57214a0a62f69924
                    data["posts"].append(post_url)
                else:
                    raise NotImplementedError(link_object, self.search_url, post_url, artist_url)
            elif isinstance(parsed := Url.parse(site), PixivPostUrl):
                data["posts"].append(parsed)
                try:
                    data["found_urls"].append(parsed.artist)
                except DeadUrlError:
                    continue
            else:
                raise NotImplementedError(site, link_object, self.search_url)

    def __external_case(self, url_groups: list[Tag], data: dict[str, list]) -> None:
        if not url_groups:
            raise NotImplementedError(self.html_data, self.search_url)

        if len(url_groups) > 1:
            raise NotImplementedError(url_groups, self.search_url)

        if "sakura.ne.jp" in (url_text := url_groups[0].text.strip()):
            self.__parse_sakura_result(url_groups[0], data)
        elif ".lofter.com" in url_text:
            self.__parse_lofter_result(url_groups[0], data)
        elif not (extracted_urls := extract_urls_from_string(url_text)):
            return
        else:
            raise NotImplementedError(url_groups, extracted_urls, self.search_url)

    @staticmethod
    def __parse_dlsite_result(url_element: Tag, data: dict[str, list]) -> None:
        url = url_element["href"]
        book = DlsiteWorkUrl.parse_and_assert(url)
        data["posts"].append(book)
        data["found_urls"].append(book.gallery)

    @staticmethod
    def __parse_fanza_result(url_element: Tag, data: dict[str, list]) -> None:
        url = url_element["href"]
        book = FanzaUrl.parse_and_assert(url)
        assert isinstance(book, PostUrl)
        data["posts"].append(book)
        data["found_urls"].append(book.gallery)

    @staticmethod
    def __parse_sakura_result(element: Tag, data: dict[str, list]) -> None:
        name, url = element.text.split("'")
        sakura_url = SakuraBlogUrl.parse_and_assert(url)
        data["primary_names"].append(name)
        data["found_urls"].append(sakura_url)

    @staticmethod
    def __parse_lofter_result(element: Tag, data: dict[str, list]) -> None:
        lofter_url = LofterPostUrl.parse_and_assert(element.text)
        data["posts"].append(lofter_url)
        data["found_urls"].append(lofter_url.gallery)


class Ascii2dSession(Session):
    MAX_CALLS_PER_SECOND = 0.5
    DEFAULT_TIMEOUT = 60

    def _reverse_search_url(self, url: str) -> list[Ascii2dArtistResult]:
        # can't use /color/md5 because sometimes the result is not cached and requires a cloudflare-protected POST
        ascii2d_url = f"https://ascii2d.net/search/url/{url}"
        try:
            response = self.get(ascii2d_url).html
        except HTTPError as e:
            if e.status_code == 502:
                logger.error("ASCII2D is having issues. Skipping check.")
                return []
            raise

        html_results = response.select(".item-box")
        if not html_results:
            if "ごく最近、このURLからのダウンロードに失敗しています。少し時間を置いてください。" in str(response):
                logger.error("ASCII2D is having issues. Skipping check.")
                return []
            else:
                raise NotImplementedError(f"Page layout might have changed: {ascii2d_url} - {response}")

        results: list[Ascii2dArtistResult] = []
        for result_html in html_results:
            if result_html.select_one(".detail-box").text.strip():
                info_box = result_html.select_one(".info-box")
                result = Ascii2dArtistResult(info_box, ascii2d_url)
                results.append(result)

        assert results, f"No parsable results for {url}"  # to make sure page layout hasn't changed
        return results

    def find_gallery(self, url: str, original_url: Url | str, original_post: DanbooruPost) -> Ascii2dArtistResult | None:
        for index, result in enumerate(self._reverse_search_url(url)):
            if result.md5 == original_post.md5:
                return result

            if index > 5:
                continue  # don't bother checking past the first 5 results

            try:
                if not result:
                    continue
            except Exception as e:
                e.add_note(f"\nHTML:\n\n{result.html_data}\n\nCaught while parsing {result.search_url}")
                raise

            original_url = Url.parse(original_url)
            if isinstance(original_url, PostAssetUrl):
                original_url = original_url.post

            if isinstance(original_url, PostUrl):
                if original_url.normalized_url in [url.normalized_url for url in result.posts]:
                    for post in result.posts:
                        if isinstance(post, NicoSeigaIllustUrl):
                            continue  # blocked outside jp
                        try:
                            result._data["found_urls"] += [post.artist]
                        except DeadUrlError:
                            continue
                    return result
                continue
            raise NotImplementedError(original_url)

        return None
