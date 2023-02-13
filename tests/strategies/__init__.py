from datetime import datetime
from typing import TypeVar

from danboorutools.models.url import ArtistUrl, AssetUrl, GalleryUrl, InfoUrl, PostUrl, RedirectUrl, Url
from tests import assert_comparison, assert_equal, assert_is_instance, assert_not


def assert_urls_are_same(lhs_value: list[Url] | list[str], rhs_value: list[Url] | list[str]) -> None:
    lhs_urls = sorted([Url.parse(u) for u in lhs_value], key=lambda u: u.normalized_url)
    rhs_urls = sorted([Url.parse(u) for u in rhs_value], key=lambda u: u.normalized_url)
    assert_equal(lhs_urls, rhs_urls)


def assert_artist_url(artist_url: Url | str,
                      /,
                      identifier: int | str,
                      is_deleted: bool,
                      names: list[str],
                      related: list[Url] | list[str],
                      post_count: int
                      ) -> ArtistUrl:
    artist_url = assert_casted(artist_url, ArtistUrl)

    assert_equal(artist_url.id, identifier)
    assert_equal(artist_url.is_deleted, is_deleted)
    assert_equal(sorted(artist_url.names), sorted(names))
    assert_urls_are_same(related, artist_url.related)

    assert_comparison(artist_url.posts, ">=", post_count)

    return artist_url


def assert_post_url(post_url: Url | str,
                    /,
                    identifier: int | str,
                    normalized_url: str,
                    gallery: GalleryUrl,
                    asset_count: int,
                    score: int,
                    created_at: datetime | str,
                    check_from_string: bool = False
                    ) -> PostUrl:
    post_url = assert_casted(post_url, PostUrl)
    assert_equal(post_url.id, identifier)
    assert_equal(post_url.normalized_url, normalized_url)
    assert_equal(post_url.gallery, gallery)
    assert_equal(post_url.created_at, created_at)
    assert_equal(len(post_url.assets), asset_count)
    assert_comparison(post_url.score, ">=", score)

    if check_from_string:
        assert_post_url_from_string(post_url.normalized_url,
                                    identifier=identifier,
                                    normalized_url=normalized_url,
                                    gallery=gallery,
                                    asset_count=asset_count,
                                    score=score,
                                    created_at=created_at)

    return post_url


def assert_post_url_from_string(post_url_string: str,
                                /,
                                identifier: int | str,
                                normalized_url: str,
                                gallery: GalleryUrl,
                                asset_count: int,
                                score: int,
                                created_at: datetime | str,
                                ) -> None:

    post_url_from_string = assert_casted(post_url_string, PostUrl)
    assert_post_url(post_url_from_string,
                    identifier=identifier,
                    normalized_url=normalized_url,
                    gallery=gallery,
                    asset_count=asset_count,
                    score=score,
                    created_at=created_at,
                    check_from_string=False)


def assert_asset_url(asset_url: Url | str,
                     /,
                     identifier: int | str,
                     normalized_url: str | None = None,
                     file_count: int = 1,
                     gallery: ArtistUrl | None = None,
                     created_at: datetime | str | None = None
                     ) -> AssetUrl:
    asset_url = assert_casted(asset_url, AssetUrl)
    asset_url_from_string = assert_casted(asset_url.normalized_url, AssetUrl)

    assert_is_instance(asset_url_from_string, type(asset_url))

    assert_equal(asset_url.id, identifier)
    assert_equal(asset_url.id, asset_url_from_string.id)

    if normalized_url:
        assert_equal(asset_url.normalized_url, normalized_url)
    assert_equal(asset_url.normalized_url, asset_url_from_string.normalized_url)

    assert_equal(len(asset_url.files), file_count)
    assert_equal(len(asset_url.files), len(asset_url_from_string.files))

    if asset_url.post and asset_url_from_string.post:
        assert_equal(asset_url.post, asset_url_from_string.post)

    if gallery:
        assert_equal(asset_url.post.gallery, gallery)
        assert_equal(asset_url.post.gallery, asset_url_from_string.post.gallery)

    if created_at:
        assert_equal(asset_url.created_at, created_at)
        assert_equal(asset_url.created_at, asset_url_from_string.created_at)

    return asset_url


def assert_asset_file(asset: AssetUrl, md5s: list[str]) -> None:
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

    assert_is_instance(redirect_url, RedirectUrl)

    redirect_to = Url.parse(redirect_to)
    assert_equal(redirect_url.resolved.normalized_url, redirect_to.normalized_url)

    return redirect_url


Casted = TypeVar("Casted", bound=Url)


def assert_casted(url: str | Url, to_type: type[Casted]) -> Casted:
    casted_url = to_type.parse(url)
    assert_is_instance(casted_url, to_type)
    return casted_url  # type: ignore[return-value]


def assert_parsed(string: str, url_type: type[Url], url_id: str | int = "") -> None:
    url = Url.parse(string)

    assert_is_instance(url, url_type)
    assert_equal(url.id, str(url_id))


def assert_parse_test_cases(url_type: type[Url]) -> None:
    for test_case in url_type.test_cases:
        parsed_url = Url.parse(test_case)
        assert_is_instance(parsed_url, url_type)
        if url_type.id_name:
            assert_not(parsed_url.id, "")
        else:
            assert_equal(parsed_url.id, "")
