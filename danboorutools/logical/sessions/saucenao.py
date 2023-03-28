import os
import re
from dataclasses import dataclass

import ring

from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.pixiv import PixivArtistUrl, PixivStaccUrl, PixivUrl
from danboorutools.models.danbooru import DanbooruPost
from danboorutools.models.url import InfoUrl, PostAssetUrl, PostUrl, Url

pixiv_id_lookup_artist_pattern = re.compile(
    r"User ID: (?P<id>\d+)Login Username: (?P<stacc>\w+)Display Username\(s\):(?P<name>.*) \(\d+\)\n",
)


@dataclass
class SaucenaoArtistResult:
    found_urls: list[InfoUrl]
    primary_names: list[str]
    secondary_names: list[str]

    def __bool__(self):
        return any([self.found_urls, self.primary_names, self.secondary_names])


class SaucenaoSession(Session):
    no_artist_indexes = [
        0,   # H-Magazines
        2,   # H-Game CG
        21,  # Anime
        36,  # Madokami
    ]

    API_KEY = os.environ["SAUCENAO_API_KEY"]
    MAX_CALLS_PER_SECOND = 0.5
    DEFAULT_TIMEOUT = 10

    @ring.lru()
    def _reverse_search_url(self, image_url: str) -> list[dict[str, dict]]:
        """Reverse search an url."""
        saucenao_url = f"https://saucenao.com/search.php?db=999&output_type=2&numres=16&url={image_url}&api_key={self.API_KEY}"
        response = self.get(saucenao_url).json()
        results = response["results"]
        if not results:
            raise NotImplementedError(response)
        return results

    def find_gallery(self, image_url: str, original_url: Url | str, original_post: DanbooruPost | None = None) -> SaucenaoArtistResult | None:
        subresults = []

        if not isinstance(original_url, Url):
            original_url = Url.parse(original_url)

        for result in self._reverse_search_url(image_url):
            if result["header"]["index_id"] in self.no_artist_indexes:
                continue

            if result["header"]["index_id"] == 9:  # danbooru
                if original_post and DanbooruPost.id_from_url(result["data"]["ext_urls"][0]) != original_post.id:
                    continue
                if subresult := self.__parse_danbooru_result(result, original_url):
                    subresults.append(subresult)
                continue

            result_data = result["data"]
            for external_url in result_data["ext_urls"]:
                match_url = Url.parse(external_url)

                # the following is required to avoid getting the updated url for old pixiv urls, which would be expensive and useless
                # and also not possible for dead urls, while for posts we can get the normalized url even if it's deleted anyway
                if isinstance(match_url, PostAssetUrl):
                    match_url = match_url.post
                if isinstance(original_url, PostAssetUrl):
                    original_url = original_url.post

                if match_url.normalized_url == original_url.normalized_url:
                    break
            else:
                continue
            break
        else:
            return self.__merge_results(*subresults) if subresults else None  # pylint: disable=no-value-for-parameter

        if isinstance(match_url, PixivUrl):
            saucenao_result = self.__parse_pixiv_result(result_data)
        else:
            raise NotImplementedError(match_url)

        self.__merge_results(saucenao_result, *subresults)
        return saucenao_result

    def __merge_results(self, saucenao_result: SaucenaoArtistResult, *subresults: SaucenaoArtistResult) -> SaucenaoArtistResult:
        for subresult in subresults:
            saucenao_result.found_urls += subresult.found_urls
            saucenao_result.primary_names += subresult.primary_names
            saucenao_result.secondary_names += subresult.secondary_names
        return saucenao_result

    def __parse_pixiv_result(self, saucenao_result: dict) -> SaucenaoArtistResult:
        pixiv_id = saucenao_result["member_id"]
        stacc = saucenao_result["member_login_name"]
        extra_urls = [PixivStaccUrl.build(stacc=stacc)] if stacc else []
        secondary_names = [stacc, f"pixiv {pixiv_id}"] if stacc else [f"pixiv {pixiv_id}"]

        pixiv_artist_url = PixivArtistUrl.build(user_id=pixiv_id)

        return SaucenaoArtistResult(
            found_urls=[pixiv_artist_url, *extra_urls],
            primary_names=[saucenao_result["member_name"]],
            secondary_names=secondary_names,
        )

    def __parse_danbooru_result(self, saucenao_result: dict[str, dict], source_from_danbooru: Url) -> SaucenaoArtistResult | None:
        source_from_saucenao = Url.parse(saucenao_result["data"]["source"].removesuffix(" (deleted)"))  # bruh

        if isinstance(source_from_danbooru, PostAssetUrl):
            source_from_danbooru = source_from_danbooru.post
        elif not isinstance(source_from_danbooru, PostUrl):
            raise NotImplementedError(saucenao_result, source_from_danbooru)

        if isinstance(source_from_saucenao, PostAssetUrl):
            source_from_saucenao = source_from_saucenao.post
        elif not isinstance(source_from_saucenao, PostUrl):
            raise NotImplementedError(saucenao_result, source_from_saucenao)

        if source_from_saucenao.normalized_url != source_from_danbooru.normalized_url:
            raise NotImplementedError(saucenao_result, source_from_saucenao, source_from_danbooru)

        result = SaucenaoArtistResult(found_urls=[], primary_names=[], secondary_names=[])

        if isinstance(source_from_saucenao, PixivUrl):
            if not (creator := saucenao_result["data"]["creator"]):
                return None  # Saucenao doesn't have it
            if "," in creator:
                return None  # saucenao database is fucked
            if creator in saucenao_result["data"]["material"]:
                return None  # as above
            if match := re.match(r"^pixiv id (\d+)$", creator):
                result.found_urls += [PixivArtistUrl.build(user_id=int(match.groups()[0]))]
            else:
                stacc = creator.replace(" ", "_")
                result.found_urls += [PixivStaccUrl.build(stacc=stacc)]
                result.secondary_names += [stacc]
        else:
            raise NotImplementedError

        return result
