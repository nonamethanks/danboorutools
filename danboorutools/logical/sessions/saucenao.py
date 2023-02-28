import os
import re
from dataclasses import dataclass
from typing import Sequence

from ratelimit import limits, sleep_and_retry

from danboorutools.exceptions import NoSaucenaoResult
from danboorutools.logical.extractors.pixiv import PixivArtistUrl, PixivStaccUrl, PixivUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.url import InfoUrl, Url
from danboorutools.util.misc import memoize

pixiv_id_lookup_artist_pattern = re.compile(
    r"User ID: (?P<id>\d+)Login Username: (?P<stacc>\w+)Display Username\(s\):(?P<name>.*) \(\d+\)\n"
)


@dataclass
class SaucenaoArtistResult:
    artist_url: InfoUrl
    extra_urls: Sequence[InfoUrl]
    primary_names: list[str]
    secondary_names: list[str]


class SaucenaoSession(Session):
    no_artist_indexes = [
        0,   # H-Magazines
        2,   # H-Game CG
        21,  # Anime
        36,  # Madokami
    ]
    imageboard_indexes = [
        9,   # Danbooru
    ]

    API_KEY = os.environ["SAUCENAO_API_KEY"]

    @memoize
    @sleep_and_retry
    @limits(calls=1, period=2)
    def _reverse_search_url(self, image_url: str) -> list[dict[str, dict]]:
        """Reverse search an url."""
        saucenao_url = f"https://saucenao.com/search.php?db=999&output_type=2&numres=16&url={image_url}&api_key={self.API_KEY}"
        response = self.get(saucenao_url).json()
        results = response["results"]
        if not results:
            raise NotImplementedError(response)
        return results

    def find_gallery(self, image_url: str, original_url: Url) -> SaucenaoArtistResult:
        results = self._reverse_search_url(image_url)
        for result in results:
            if result["header"]["index_id"] in self.no_artist_indexes:
                continue

            if result["header"]["index_id"] in self.imageboard_indexes:
                continue

            result_data = result["data"]
            if any((match_url := Url.parse(ext_url)).normalized_url == original_url.normalized_url for ext_url in result_data["ext_urls"]):
                break
        else:
            raise NoSaucenaoResult(results)

        if isinstance(match_url, PixivUrl):
            pixiv_id = result_data["member_id"]
            stacc = result_data["member_login_name"]

            pixiv_artist_url = Url.build(PixivArtistUrl, user_id=pixiv_id)
            stacc_url = Url.build(PixivStaccUrl, stacc=stacc)

            saucenao_result = SaucenaoArtistResult(
                artist_url=pixiv_artist_url,
                extra_urls=[stacc_url],
                primary_names=[result_data["member_name"]],
                secondary_names=[stacc, f"pixiv {pixiv_id}"],
            )
        else:
            raise NotImplementedError(match_url)

        return saucenao_result
