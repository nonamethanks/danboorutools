import os
import re

from pydantic import ConfigDict, validator

from danboorutools import logger
from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.pixiv import PixivArtistUrl, PixivStaccUrl, PixivUrl
from danboorutools.models.danbooru import DanbooruPost
from danboorutools.models.url import InfoUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import BaseModel

pixiv_id_lookup_artist_pattern = re.compile(
    r"User ID: (?P<id>\d+)Login Username: (?P<stacc>\w+)Display Username\(s\):(?P<name>.*) \(\d+\)\n",
)


class SaucenaoArtistResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    found_urls: list[InfoUrl]
    primary_names: list[str]
    secondary_names: list[str]

    def __bool__(self):
        return any([self.found_urls, self.primary_names, self.secondary_names])


class _SaucenaoHeaderResponse(BaseModel):
    similarity: float
    thumbnail: str
    index_id: int
    index_name: str
    dupes: int
    hidden: int

    # index 5 - pixiv


class _SaucenaoBaseDataResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ext_urls: list[str] | None = None


class _NotImplementedDataResponse(_SaucenaoBaseDataResponse):
    model_config = ConfigDict(extra="allow")

    def artist_result(self) -> SaucenaoArtistResult:
        raise NotImplementedError(self)


class _SaucenaoPixivData(_SaucenaoBaseDataResponse):
    # index 5 - pixiv
    title: str
    pixiv_id: int
    member_name: str
    member_id: int
    member_login_name: str | None = None  # stacc

    @property
    def artist_result(self) -> SaucenaoArtistResult:
        secondary_names = [f"pixiv {self.member_id}"]
        if self.member_login_name:
            secondary_names.append(self.member_login_name)

        extra_urls = [PixivArtistUrl.build(user_id=self.member_id)]
        if self.member_login_name:
            extra_urls += [PixivStaccUrl.build(stacc=self.member_login_name)]

        return SaucenaoArtistResult(
            primary_names=[self.member_name],
            secondary_names=secondary_names,
            found_urls=extra_urls,
        )


class _SaucenaoDanbooruData(_SaucenaoBaseDataResponse):
    # index 9 - danbooru
    danbooru_id: int
    gelbooru_id: int | None = None
    sankaku_id: int | None = None

    creator: str
    material: str
    characters: str
    source: str
    ext_urls: list[str]

    @property
    def danbooru_post_id(self) -> int:
        return DanbooruPost.id_from_url(self.ext_urls[0])  # pylint: disable=unsubscriptable-object

    @property
    def artist_result(self) -> SaucenaoArtistResult:
        if (_source := self.source.removesuffix(" (deleted)")).startswith("file://"):  # bruh
            return None
        source_from_saucenao = Url.parse(_source)

        if isinstance(source_from_saucenao, PostAssetUrl):
            source_from_saucenao = source_from_saucenao.post
        elif not isinstance(source_from_saucenao, PostUrl):
            raise NotImplementedError(self, source_from_saucenao)

        result = SaucenaoArtistResult(found_urls=[source_from_saucenao.artist], primary_names=[], secondary_names=[])

        if not self.creator:
            return result  # Saucenao doesn't have it
        if "," in self.creator:
            return result  # saucenao database is fucked
        if self.creator.strip() + "," in self.material or self.material.strip() == self.creator.strip():
            return result  # as above, sometimes copyrights end up in the creator field

        if isinstance(source_from_saucenao, PixivUrl):
            if match := re.match(r"^pixiv id (\d+)$",  self.creator):
                result.found_urls += [PixivArtistUrl.build(user_id=int(match.groups()[0]))]
            else:
                stacc = self.creator.replace(" ", "_")
                result.found_urls += [PixivStaccUrl.build(stacc=stacc)]
                result.secondary_names += [stacc]
        else:
            raise NotImplementedError(self)

        return result


class _SaucenaoApiResult(BaseModel):
    header: _SaucenaoHeaderResponse
    data: _SaucenaoPixivData | _SaucenaoDanbooruData | _NotImplementedDataResponse

    @validator("data", pre=True)
    @classmethod
    def parse_data(cls, value: dict, values: dict) -> _SaucenaoPixivData | _SaucenaoDanbooruData:
        if values["header"].index_id == 5:
            return _SaucenaoPixivData(**value)
        elif values["header"].index_id == 9:
            return _SaucenaoDanbooruData(**value)
        else:
            return _NotImplementedDataResponse(**value)


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

    def _reverse_search_url(self, image_url: str) -> list[_SaucenaoApiResult]:
        """Reverse search an url."""
        saucenao_url = f"https://saucenao.com/search.php?db=999&output_type=2&numres=16&url={image_url}&api_key={self.API_KEY}"
        response = self.get_json(saucenao_url)
        results = response["results"]
        if not results:
            raise NotImplementedError(response)
        return [_SaucenaoApiResult(**result) for result in results]

    def find_gallery(self, image_url: str, original_url: Url | str, original_post: DanbooruPost | None = None) -> SaucenaoArtistResult | None:
        subresults = []

        if not isinstance(original_url, Url):
            original_url = Url.parse(original_url)

        for result in self._reverse_search_url(image_url):
            if result.header.index_id in self.no_artist_indexes:
                continue

            if isinstance(result.data, _SaucenaoDanbooruData):
                if result.data.danbooru_post_id == original_post.id:
                    subresults.append(result.data.artist_result)
                continue

            if not result.data.ext_urls:
                continue

            for external_url in result.data.ext_urls:
                # check if the url that saucenao has matches the danbooru source artist
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
            logger.debug("No saucenao result matches the right artist.")
            return self.__merge_results(*subresults) if subresults else None  # pylint: disable=no-value-for-parameter

        artist_result = result.data.artist_result
        self.__merge_results(artist_result, *subresults)
        return artist_result

    def __merge_results(self, saucenao_result: SaucenaoArtistResult, *subresults: SaucenaoArtistResult) -> SaucenaoArtistResult:
        for subresult in subresults:
            saucenao_result.found_urls += subresult.found_urls
            saucenao_result.primary_names += subresult.primary_names
            saucenao_result.secondary_names += subresult.secondary_names
        return saucenao_result
