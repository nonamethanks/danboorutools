from datetime import datetime
from typing import Callable, TypeVar

from danboorutools.logical.parsers import UrlParser
from danboorutools.models.url import ArtistUrl, GalleryUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from tests import assert_comparison, assert_equal


def assert_urls_are_same(lhs_value: list[Url] | list[str], rhs_value: list[Url] | list[str]) -> None:
    lhs_urls = sorted([Url.parse(u) for u in lhs_value], key=lambda u: u.normalized_url)  # type: ignore[arg-type]
    rhs_urls = sorted([Url.parse(u) for u in rhs_value], key=lambda u: u.normalized_url)  # type: ignore[arg-type]
    assert_equal(lhs_urls, rhs_urls)


def assert_artist_url(artist_url: Url | str,
                      /,
                      url_type: type[ArtistUrl],
                      is_deleted: bool,
                      names: list[str],
                      related: list[Url] | list[str],
                      post_count: int,
                      normalized_url: str | None = None,
                      **url_properties
                      ) -> ArtistUrl:
    parsed_artist_url = assert_casted(artist_url, url_type)

    if normalized_url:
        assert_equal(parsed_artist_url.normalized_url, normalized_url)
    elif isinstance(artist_url, str):
        assert_equal(parsed_artist_url.normalized_url, artist_url)

    assert_equal(parsed_artist_url.is_deleted, is_deleted)
    assert_equal(sorted(parsed_artist_url.names), sorted(names))
    assert_urls_are_same(related, parsed_artist_url.related)

    assert_comparison(parsed_artist_url.posts, ">=", post_count)

    for key, value in url_properties.items():
        assert_equal(getattr(parsed_artist_url, key), value)

    return parsed_artist_url


def assert_post_url(post_url: Url | str,
                    /,
                    url_type: type[PostUrl],
                    asset_count: int,
                    score: int,
                    created_at: datetime | str,
                    gallery: GalleryUrl | None = None,
                    normalized_url: str | None = None,
                    **kwargs,
                    ) -> PostUrl:
    parsed_post_url = assert_casted(post_url, url_type)

    if normalized_url:
        assert_equal(parsed_post_url.normalized_url, normalized_url)
    elif isinstance(post_url, str):
        assert_equal(parsed_post_url.normalized_url, post_url)
    if gallery:
        assert_equal(parsed_post_url.gallery, gallery)
    assert_equal(parsed_post_url.created_at, created_at)
    assert_equal(len(parsed_post_url.assets), asset_count)
    assert_comparison(parsed_post_url.score, ">=", score)

    for key, value in kwargs.items():
        assert_equal(getattr(parsed_post_url, key), value)

    return parsed_post_url


def assert_asset_url(asset_url: Url | str,
                     /,
                     url_type: type[PostAssetUrl],
                     normalized_url: str | None = None,
                     file_count: int = 1,
                     created_at: datetime | str | None = None,
                     post: PostUrl | None = None,
                     **kwargs,
                     ) -> PostAssetUrl:
    asset_url = assert_casted(asset_url, url_type)

    if normalized_url:
        assert_equal(asset_url.normalized_url, normalized_url)

    if post:
        assert_equal(post, asset_url.post)

    assert_equal(len(asset_url.files), file_count)

    if created_at:
        assert_equal(asset_url.created_at, created_at)

    for key, value in kwargs.items():
        assert_equal(getattr(asset_url, key), value)

    return asset_url


def assert_asset_file(asset: PostAssetUrl, md5s: list[str]) -> None:
    files = asset.files
    assert_equal(sorted([f.md5 for f in files]), sorted(md5s))

    for file in files:
        file.delete()


def assert_info_url(info_url: Url | str, related: list[Url] | list[str], names: list[str]) -> InfoUrl:
    info_url = assert_casted(info_url, InfoUrl)

    assert_urls_are_same(info_url.related, related)
    assert_equal(sorted(info_url.names), sorted(names))

    return info_url


def assert_redirect_url(redirect_url: Url | str, redirect_to: Url | str) -> RedirectUrl:
    redirect_url = assert_casted(redirect_url, RedirectUrl)

    assert isinstance(redirect_url, RedirectUrl)

    redirect_to = Url.parse(redirect_to)
    assert_equal(redirect_url.resolved.normalized_url, redirect_to.normalized_url)

    return redirect_url


Casted = TypeVar("Casted", bound=Url)


def assert_casted(url: str | Url, to_type: type[Casted]) -> Casted:
    casted_url = to_type.parse(url)
    assert isinstance(casted_url, to_type)
    return casted_url  # type: ignore[return-value]


def assert_parsed(string: str, url_type: type[Url], **kwargs) -> None:
    url = Url.parse(string)

    assert isinstance(url, url_type)
    for key, value in kwargs.items():
        assert_equal(getattr(url, key), value)


def prune_cache(method: Callable) -> None:
    UrlParser.parse.cache_clear()
    Url.parse.cache_clear()  # type: ignore[attr-defined]
    method()


def generate_artist_test_suite(url_type: type[ArtistUrl],
                               url: str,
                               names: list[str],
                               related: list[str],
                               post_count: int,
                               normalized_url: str | None = None,
                               post: dict | None = None,
                               **url_properties,
                               ) -> dict:

    artist = assert_casted(url, url_type)

    def _run_artist_test() -> None:
        _artist = assert_artist_url(
            artist,
            url_type=url_type,
            is_deleted=False,
            names=names,
            normalized_url=normalized_url,
            related=related,
            post_count=post_count,
            **url_properties
        )

        if post:
            assert any(post["url"] == found_post.normalized_url for found_post in _artist.posts)

    tests = {"artist": _run_artist_test}

    if post:
        tests |= generate_post_test_suite(
            gallery=artist,
            **post,
        )

    return tests


def generate_post_test_suite(url_type: type[PostUrl],
                             url: str,
                             asset_count: int,
                             score: int,
                             created_at: datetime | str,
                             gallery: GalleryUrl | None = None,
                             asset: dict | None = None,
                             **kwargs,
                             ) -> dict:
    post = assert_casted(url, url_type)

    def _run_post_test() -> None:
        _post = assert_post_url(
            url,
            url_type=url_type,
            gallery=gallery,
            asset_count=asset_count,
            score=score,
            created_at=created_at,
            **kwargs,
        )
        if asset:
            assert any(asset["url"] == found_asset.normalized_url for found_asset in _post.assets)

    tests = {"post": _run_post_test}

    if asset:
        tests |= generate_asset_test_suite(
            post=post,
            **asset,
        )

    return tests


def generate_asset_test_suite(url_type: type[PostAssetUrl],
                              url: str,
                              file_md5: str,
                              post: PostUrl | None = None,
                              **kwargs,
                              ) -> dict:

    def _run_asset_test() -> None:
        asset = assert_asset_url(
            url,
            url_type=url_type,
            post=post,
            **kwargs,
        )

        if file_md5:
            assert file_md5 in [f.md5 for f in asset.files]

    tests = {"asset": _run_asset_test}

    return tests
