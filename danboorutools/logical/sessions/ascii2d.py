from dataclasses import dataclass

from ratelimit import limits, sleep_and_retry

from danboorutools.logical.extractors.twitter import TwitterArtistUrl, TwitterIntentUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.danbooru import DanbooruPost
from danboorutools.models.url import InfoUrl, PostUrl, Url
from danboorutools.util.misc import memoize


@dataclass
class _Result:
    md5: str
    site: str
    artist_name: str
    creator_url: InfoUrl
    post_url: PostUrl


@dataclass
class Ascii2dArtistResult:
    primary_url: InfoUrl
    extra_urls: list[InfoUrl]
    primary_names: list[str]
    secondary_names: list[str]


class Ascii2dSession(Session):
    @memoize
    @sleep_and_retry
    @limits(calls=1, period=2)
    def _reverse_search_url(self, url: str) -> list[_Result]:
        # can't use /color/md5 because sometimes the result is not cached and requires a cloudflare-protected POST
        ascii2d_url = f"https://ascii2d.net/search/url/{url}"
        response = self.get_html(ascii2d_url)

        assert (results := response.select(".item-box"))
        data: list[_Result] = []

        for result_html in results:
            result_info_box = result_html.select_one(".info-box")
            md5 = result_info_box.select_one(".hash").text
            for url_group in result_info_box.select(".detail-box h6"):
                site = url_group.select_one("small").text
                post_url = Url.parse(url_group.select("a")[0]["href"])
                artist_element = url_group.select("a")[1]
                creator_url = Url.parse(artist_element["href"])
                artist_name = artist_element.text
                assert isinstance(post_url, PostUrl), (post_url, ascii2d_url)
                assert isinstance(creator_url, InfoUrl), (creator_url, ascii2d_url)
                data.append(_Result(md5=md5, site=site, artist_name=artist_name, creator_url=creator_url, post_url=post_url))

        assert data  # to make sure page layout hasn't changed
        return data

    def find_gallery(self, url: str, original_url: Url | str, original_post: DanbooruPost) -> Ascii2dArtistResult | None:
        for result in self._reverse_search_url(url):
            if result.md5 != original_post.md5 and result.post_url.normalized_url != Url.parse(original_url).normalized_url:
                continue

            if result.site == "twitter":
                assert isinstance(result.creator_url, TwitterIntentUrl), result
                return Ascii2dArtistResult(
                    primary_url=Url.build(TwitterArtistUrl, username=result.artist_name),
                    extra_urls=[result.creator_url],
                    primary_names=[],  # no need to populate these, they're extractable by the urls themselves
                    secondary_names=[],
                )
            elif result.site == "pixiv":
                return Ascii2dArtistResult(
                    primary_url=result.creator_url,
                    extra_urls=[],
                    primary_names=[result.artist_name],
                    secondary_names=[],
                )
            else:
                raise NotImplementedError(result)
        else:
            return None
