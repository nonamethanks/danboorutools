import re
from datetime import datetime
from typing import Any, TypeVar

from danboorutools.models.url import ArtistUrl, GalleryUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.time import datetime_from_string


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
    assert isinstance(casted_url, to_type)
    return casted_url


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
        assert len(gallery.posts) >= post_count

    if posts is not None:
        found_posts = gallery.posts
        for post in posts:
            assert Url.parse(post) in found_posts

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
                    created_at: datetime | str,
                    asset_count: int,
                    score: int,
                    assets: list[str | re.Pattern[str]] | None = None,
                    md5s: list[str] | None = None,
                    is_deleted: bool = False,
                    ) -> PostUrlTypeVar:

    post = assert_url(url=url, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)

    assert_equal(post.created_at, datetime_from_string(created_at))
    assert_equal(len(post.assets), asset_count)
    assert post.score >= score

    if assets is not None:
        found_assets = post.assets
        for asset in assets:
            if isinstance(asset, str):
                assert Url.parse(asset) in found_assets
            else:
                assert any(re.search(asset, found_asset.normalized_url) for found_asset in found_assets)

    if md5s is not None:
        found_md5s = [_file.md5 for asset in post.assets for _file in asset.files]
        assert all(md5 in found_md5s for md5 in md5s), (md5s, found_md5s)

    return post


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
        assert all(md5 in found_md5s for md5 in md5s), (md5s, found_md5s)

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


def assert_equal(lhv: Any, rhv: Any) -> None:  # noqa: ANN401 # SHUT THE FUCK UP
    # ward is a piece of shit that won't pretty-print asserts inside an import, so this has to be used
    # the alternative is killing myself while trying to make py-fucking-test work
    assert lhv == rhv
