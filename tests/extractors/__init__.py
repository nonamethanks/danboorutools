import inspect
import re
from datetime import datetime
from pathlib import Path
from typing import TypeVar

from danboorutools.models.url import ArtistUrl, GalleryUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import class_name_to_string
from danboorutools.util.time import datetime_from_string
from tests import assert_equal, assert_gte, assert_in, assert_isinstance, assert_match_in, generate_ward_test


def assert_urls_are_same(lhs_value: list[Url] | list[str], rhs_value: list[Url] | list[str]) -> None:
    lhs_urls = sorted([Url.parse(u) for u in lhs_value], key=lambda u: u.normalized_url)  # type: ignore[arg-type]
    rhs_urls = sorted([Url.parse(u) for u in rhs_value], key=lambda u: u.normalized_url)  # type: ignore[arg-type]
    assert_equal(lhs_urls, rhs_urls)


###########################################################

UrlTypeVar = TypeVar("UrlTypeVar", bound=Url)
GalleryUrlTypeVar = TypeVar("GalleryUrlTypeVar", bound=GalleryUrl)
ArtistUrlTypeVar = TypeVar("ArtistUrlTypeVar", bound=ArtistUrl)
InfoUrlTypeVar = TypeVar("InfoUrlTypeVar", bound=InfoUrl)
PostUrlTypeVar = TypeVar("PostUrlTypeVar", bound=PostUrl)
PostAssetUrlTypeVar = TypeVar("PostAssetUrlTypeVar", bound=PostAssetUrl)
RedirectUrlTypeVar = TypeVar("RedirectUrlTypeVar", bound=RedirectUrl)


def assert_casted(url: str | Url, to_type: type[UrlTypeVar]) -> UrlTypeVar:
    casted_url = to_type.parse(url)
    assert_isinstance(casted_url, to_type)
    return casted_url  # type: ignore[return-value]


###########################################################


def assert_url(url: str,
               url_type: type[UrlTypeVar],
               url_properties: dict,
               is_deleted: bool = False,
               ) -> UrlTypeVar:
    parsed_url = assert_casted(url, url_type)

    for property_name, expected_value in url_properties.items():
        actual_value = getattr(parsed_url, property_name)
        assert_equal(actual_value, expected_value)

    assert_equal(parsed_url.is_deleted, is_deleted)
    return parsed_url


def assert_gallery_url(url: str,
                       url_type: type[GalleryUrlTypeVar],
                       url_properties: dict,
                       post_count: int | None = None,
                       posts: list[str] | None = None,
                       is_deleted: bool = False,
                       ) -> GalleryUrlTypeVar:
    gallery = assert_url(url=url, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)
    if post_count is not None:
        assert_gte(len(gallery.posts), post_count)

    if posts is not None:
        found_posts = gallery.posts
        for post in posts:
            assert_in(Url.parse(post), found_posts)

    return gallery


def assert_artist_url(url: str,
                      url_type: type[ArtistUrlTypeVar],
                      url_properties: dict,
                      primary_names: list[str],
                      secondary_names: list[str],
                      related: list[str],
                      post_count: int | None = None,
                      posts: list[str] | None = None,
                      is_deleted: bool = False,
                      ) -> ArtistUrlTypeVar:

    artist = assert_gallery_url(
        url=url,
        url_type=url_type,
        url_properties=url_properties,
        post_count=post_count,
        is_deleted=is_deleted,
        posts=posts,
    )

    assert_info_url(
        url=url,
        url_type=url_type,
        url_properties=url_properties,
        primary_names=primary_names,
        secondary_names=secondary_names,
        related=related,

    )

    return artist


def assert_post_url(url: str,
                    url_type: type[PostUrlTypeVar],
                    url_properties: dict,
                    created_at: datetime | str | None = None,
                    asset_count: int | None = None,
                    score: int | None = None,
                    assets: list[str | re.Pattern[str]] | None = None,
                    md5s: list[str] | None = None,
                    is_deleted: bool = False,
                    gallery: Url | str | None = None,
                    ) -> None:

    def _assert_post_url(url=url,
                         url_type=url_type,
                         url_properties=url_properties,
                         created_at=created_at,
                         asset_count=asset_count,
                         score=score,
                         assets=assets,
                         md5s=md5s,
                         is_deleted=is_deleted,
                         gallery=gallery) -> None:

        post = assert_url(url=url, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)

        if created_at:
            assert_equal(post.created_at, datetime_from_string(created_at))
        if asset_count:
            assert_equal(len(post.assets), asset_count)
        if score:
            assert_gte(post.score, score)

        if assets is not None:
            found_assets = post.assets
            for asset in assets:
                if isinstance(asset, str):
                    assert_in(Url.parse(asset), found_assets)
                else:
                    assert_match_in(asset, [a.normalized_url for a in found_assets])

        if md5s is not None:
            found_md5s = [_file.md5 for asset in post.assets for _file in asset.files]
            assert all(md5 in found_md5s for md5 in md5s), (md5s, found_md5s)

        if gallery:
            gallery = Url.parse(gallery)
            assert_equal(post.gallery.normalized_url, gallery.normalized_url)

    caller = inspect.stack()[1]
    abs_path = Path(caller.filename).resolve()
    domain = abs_path.stem.removesuffix("_test")
    url_type_str = class_name_to_string(url_type).split("_")[-2]  # as if...

    generate_ward_test(
        _assert_post_url,
        description=f"Scrape {url_type.__name__}: {url}",
        tags=["scraping", domain, url_type_str]
    )


def assert_asset_url(url: str,
                     url_type: type[PostAssetUrlTypeVar],
                     url_properties: dict,
                     file_count: int = 1,
                     created_at: datetime | str | None = None,
                     md5s: list[str] | None = None,
                     is_deleted: bool = False,
                     ) -> PostAssetUrlTypeVar:

    asset = assert_url(url=url, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)

    assert_equal(len(asset.files), file_count)

    if created_at:
        assert_equal(asset.created_at, datetime_from_string(created_at))

    if md5s:
        found_md5s = [_file.md5 for _file in asset.files]
        for md5 in md5s:
            assert_in(md5, found_md5s)

    return asset


def assert_info_url(url: str,
                    url_type: type[InfoUrlTypeVar],
                    url_properties: dict,
                    related: list[str],
                    primary_names: list[str],
                    secondary_names: list[str],
                    is_deleted: bool = False,
                    ) -> InfoUrlTypeVar:

    info_url = assert_url(url=url, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)

    assert_urls_are_same(info_url.related, related)
    assert_equal(sorted(info_url.primary_names), sorted(primary_names))
    assert_equal(sorted(info_url.secondary_names), sorted(secondary_names))

    return info_url


def assert_redirect_url(url: str,
                        url_type: type[RedirectUrlTypeVar],
                        url_properties: dict,
                        redirects_to: str,
                        is_deleted: bool = False,
                        ) -> RedirectUrlTypeVar:

    redirect_url = assert_url(url=url, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)
    redirect_to = Url.parse(redirects_to)

    assert_equal(redirect_url.resolved.normalized_url, redirect_to.normalized_url)

    return redirect_url


def generate_parsing_suite(urls: dict[type[UrlTypeVar], dict]) -> None:
    caller = inspect.stack()[1]
    abs_path = Path(caller.filename).resolve()
    domain = abs_path.stem.removesuffix("_test")

    for url_type, string_and_normalization in urls.items():
        url_type_str = url_type.__name__.split(".")[-1]

        for url_string, expected_normalization in string_and_normalization.items():

            def parse(url_type=url_type, url_string=url_string) -> None:
                parsed_url = Url.parse(url_string)
                assert_isinstance(parsed_url, url_type)

            generate_ward_test(
                parse,
                description=f"Parse {url_type_str}: {url_string}",
                tags=["parsing", domain]
            )

            def normalize(url_string=url_string, expected_normalization=expected_normalization) -> None:
                parsed_url = Url.parse(url_string)
                assert_equal(parsed_url.normalized_url, expected_normalization)

            generate_ward_test(
                normalize,
                description=f"Normalize {url_type_str}: {url_string}",
                tags=["parsing", "normalization", domain],
                expected_failure=not expected_normalization,
            )
