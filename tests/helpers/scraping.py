import datetime
import re
from typing import TypeVar

from danboorutools.models.url import ArtistUrl, GalleryUrl, InfoUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.time import datetime_from_string

UrlTypeVar = TypeVar("UrlTypeVar", bound=Url)


def generate_artist_test(*,  # noqa: PLR0913
                         url_string: str,
                         url_type: type[ArtistUrl],
                         url_properties: dict,
                         primary_names: list[str],
                         secondary_names: list[str],
                         related: list[str],
                         post_count: int | None = None,
                         posts: list[str] | None = None,
                         is_deleted: bool = False) -> None:

    artist_url = _assert_parsed(url_string=url_string, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)
    _assert_gallery_data(artist_url, post_count=post_count, posts=posts)
    _assert_info_data(artist_url, primary_names=primary_names, secondary_names=secondary_names, related=related)


def generate_gallery_test(*,  # noqa: PLR0913
                         url_string: str,
                         url_type: type[GalleryUrl],
                         url_properties: dict,
                         post_count: int | None = None,
                         posts: list[str] | None = None,
                         is_deleted: bool = False) -> None:

    gallery_url = _assert_parsed(url_string=url_string, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)
    _assert_gallery_data(gallery_url, post_count=post_count, posts=posts)


def generate_redirect_test(*,
                           url_string: str,
                           url_type: type[RedirectUrl],
                           url_properties: dict,
                           redirects_to: str,
                           is_deleted: bool = False,
                           ) -> None:

    redirect_url = _assert_parsed(url_string=url_string, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)
    redirect_to = Url.parse(redirects_to)

    assert redirect_url.resolved.normalized_url == redirect_to.normalized_url


def generate_info_test(*,  # noqa: PLR0913
                         url_string: str,
                         url_type: type[InfoUrl],
                         url_properties: dict,
                         primary_names: list[str],
                         secondary_names: list[str],
                         related: list[str],
                         is_deleted: bool = False) -> None:

    info_url = _assert_parsed(url_string=url_string, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)
    _assert_info_data(info_url, primary_names=primary_names, secondary_names=secondary_names, related=related)


def generate_post_test(*,  # noqa: PLR0913
                       url_string: str,
                       url_type: type[PostUrl],
                       url_properties: dict,
                       created_at: datetime.datetime | str | None = None,
                       asset_count: int | None = None,
                       score: int | None = None,
                       assets: list[str | re.Pattern[str]] | None = None,
                       md5s: list[str] | None = None,
                       is_deleted: bool = False,
                       gallery: Url | str | None = None) -> None:

    post = _assert_parsed(url_string=url_string, url_type=url_type, url_properties=url_properties, is_deleted=is_deleted)

    if created_at is not None:
        assert post.created_at == datetime_from_string(created_at)
    if asset_count is not None:
        assert len(post.assets) == asset_count
    if score is not None:
        assert post.score >= score

    if assets is not None:
        found_assets = post.assets
        for expected_asset in assets:
            if isinstance(expected_asset, str):
                assert Url.parse(expected_asset) in found_assets
            else:
                assert any(re.search(expected_asset, element.normalized_url) for element in found_assets)

    if md5s is not None:
        found_md5s = [_file.md5 for asset in post.assets for _file in asset.files]
        assert all(md5 in found_md5s for md5 in md5s), (md5s, found_md5s)

    if gallery is not None:
        gallery = Url.parse(gallery)
        assert post.gallery.normalized_url == gallery.normalized_url


def _assert_parsed(url_string: str,
                   url_type: type[UrlTypeVar],
                   url_properties: dict,
                   is_deleted: bool = False,
                   ) -> UrlTypeVar:

    url = Url.parse(url_string)

    assert isinstance(url, url_type)

    for property_name, expected_value in url_properties.items():
        actual_value = getattr(url, property_name)
        assert actual_value == expected_value

    assert url.is_deleted == is_deleted
    return url


def _assert_gallery_data(gallery_url: GalleryUrl,
                         post_count: int | None = None,
                         posts: list[str] | None = None) -> None:
    if not post_count and not posts:
        return

    found_posts = gallery_url.extract_posts()

    if post_count is not None:
        assert len(found_posts) >= post_count

    if posts is not None:
        for post in posts:
            assert Url.parse(post) in found_posts


def _assert_info_data(info_url: InfoUrl,
                      primary_names: list[str],
                      secondary_names: list[str],
                      related: list[str]) -> None:
    if related is not None:
        parsed_related = [Url.parse(u) for u in related]
        assert sorted(info_url.related, key=lambda u: u.normalized_url) == sorted(parsed_related, key=lambda u: u.normalized_url)
    if primary_names is not None:
        assert sorted(info_url.primary_names) == sorted(primary_names)
    if secondary_names is not None:
        assert sorted(info_url.secondary_names) == sorted(secondary_names)
