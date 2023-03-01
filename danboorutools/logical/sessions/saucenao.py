import os
import re
from dataclasses import dataclass

from ratelimit import limits, sleep_and_retry

from danboorutools.logical.extractors.pixiv import PixivArtistUrl, PixivStaccUrl, PixivUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.danbooru import DanbooruPost
from danboorutools.models.url import InfoUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import memoize

pixiv_id_lookup_artist_pattern = re.compile(
    r"User ID: (?P<id>\d+)Login Username: (?P<stacc>\w+)Display Username\(s\):(?P<name>.*) \(\d+\)\n"
)


@dataclass
class SaucenaoArtistResult:
    primary_url: InfoUrl
    extra_urls: list[InfoUrl]
    primary_names: list[str]
    secondary_names: list[str]


@dataclass
class _SubResult:
    extra_urls: list[InfoUrl]
    primary_names: list[str]
    secondary_names: list[str]


class SaucenaoSession(Session):
    no_artist_indexes = [
        0,   # H-Magazines
        2,   # H-Game CG
        21,  # Anime
        36,  # Madokami
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

    def find_gallery(self, image_url: str, original_url: Url | str, original_post: DanbooruPost | None = None) -> SaucenaoArtistResult | None:
        subresults: list[_SubResult] = []
        if not isinstance(original_url, Url):
            original_url = Url.parse(original_url)

        results = self._reverse_search_url(image_url)
        for result in results:
            if result["header"]["index_id"] in self.no_artist_indexes:
                continue

            if result["header"]["index_id"] == 9:  # danbooru
                if original_post and DanbooruPost.id_from_url(result["data"]["ext_urls"][0]) != original_post.id:
                    continue
                if subresult := self.__parse_danbooru_result(result, original_url):
                    subresults.append(subresult)
                continue

            result_data = result["data"]
            if any((match_url := Url.parse(ext_url)).normalized_url == original_url.normalized_url for ext_url in result_data["ext_urls"]):
                break
        else:
            if subresults:
                first_url = subresults[0].extra_urls.pop(0)
                saucenao_result = SaucenaoArtistResult(primary_url=first_url, **subresults[0].__dict__)
                self.__merge_results(saucenao_result, subresults[1:])
                return saucenao_result

            else:
                return None

        if isinstance(match_url, PixivUrl):
            saucenao_result = self.__parse_pixiv_result(result_data)
        else:
            raise NotImplementedError(match_url)

        self.__merge_results(saucenao_result, subresults)
        return saucenao_result

    def __merge_results(self, saucenao_result: SaucenaoArtistResult, subresults: list[_SubResult]) -> None:
        for subresult in subresults:
            saucenao_result.extra_urls += subresult.extra_urls
            saucenao_result.primary_names += subresult.primary_names
            saucenao_result.secondary_names += subresult.secondary_names

    def __parse_pixiv_result(self, saucenao_result: dict) -> SaucenaoArtistResult:
        pixiv_id = saucenao_result["member_id"]
        stacc = saucenao_result["member_login_name"]

        pixiv_artist_url = Url.build(PixivArtistUrl, user_id=pixiv_id)
        stacc_url = Url.build(PixivStaccUrl, stacc=stacc)

        result = SaucenaoArtistResult(
            primary_url=pixiv_artist_url,
            extra_urls=[stacc_url],
            primary_names=[saucenao_result["member_name"]],
            secondary_names=[stacc, f"pixiv {pixiv_id}"],
        )

        return result

    def __parse_danbooru_result(self, saucenao_result: dict[str, dict], source_from_danbooru: Url) -> _SubResult | None:
        source_from_saucenao = Url.parse(saucenao_result["data"]["source"])
        if isinstance(source_from_danbooru, PostAssetUrl):
            source_from_danbooru = source_from_danbooru.post

        if source_from_saucenao.normalized_url != source_from_danbooru.normalized_url:
            if isinstance(source_from_saucenao, PostAssetUrl) and isinstance(source_from_danbooru, PostUrl):
                source_from_saucenao = source_from_saucenao.post

                if source_from_saucenao.normalized_url != source_from_danbooru.normalized_url:
                    raise NotImplementedError(saucenao_result, source_from_saucenao, source_from_danbooru)
            else:
                raise NotImplementedError(saucenao_result)

        result = _SubResult(extra_urls=[], primary_names=[], secondary_names=[])

        if isinstance(source_from_saucenao, PixivUrl):
            if not saucenao_result["data"]["creator"]:
                return None  # Saucenao doesn't have it
            stacc = saucenao_result["data"]["creator"].replace(" ", "_")
            result.extra_urls += [Url.build(PixivStaccUrl, stacc=stacc)]
            result.secondary_names += [stacc]
        else:
            raise NotImplementedError

        return result
