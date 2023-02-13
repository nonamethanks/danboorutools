from datetime import datetime

from danboorutools.models.url import ArtistUrl, AssetUrl, GalleryUrl, PostUrl, Url
from tests import assert_comparison, assert_equal, assert_is_instance


def assert_parsed(string: str, url_type: type[Url], url_id: str | int | None = None) -> None:
    url = Url.parse(string)

    assert_is_instance(url, url_type)
    if url_id:
        assert_equal(url.id, str(url_id))
    else:
        assert_equal(url.id, None)


def assert_artist_url(url_string: str,
                      /,
                      is_deleted: bool,
                      names: list[str],
                      related: list[Url | str],
                      post_count: int
                      ) -> ArtistUrl:
    artist_url: ArtistUrl = Url.parse(url_string)  # type: ignore[assignment]
    assert_is_instance(artist_url, ArtistUrl)

    assert_equal(artist_url.is_deleted, is_deleted)
    assert_equal(artist_url.names, names)

    related_urls = [Url.parse(u) for u in related]
    assert_equal(sorted(related_urls, key=lambda u: u.normalized_url), sorted(artist_url.related, key=lambda u: u.normalized_url))

    assert_comparison(artist_url.posts, ">=", post_count)

    return artist_url


def assert_post_url(post_url: PostUrl,
                    /,
                    normalized_url: str,
                    gallery: GalleryUrl,
                    asset_count: int,
                    score: int,
                    created_at: datetime | str,
                    check_from_string: bool = False
                    ) -> PostUrl:
    assert_is_instance(post_url, PostUrl)
    assert_equal(post_url.normalized_url, normalized_url)
    assert_equal(post_url.gallery, gallery)
    assert_equal(post_url.created_at, created_at)
    assert_equal(len(post_url.assets), asset_count)
    assert_comparison(post_url.score, ">=", score)

    if check_from_string:
        assert_post_url_from_string(post_url.normalized_url,
                                    normalized_url=normalized_url,
                                    gallery=gallery,
                                    asset_count=asset_count,
                                    score=score,
                                    created_at=created_at)

    return post_url


def assert_post_url_from_string(post_url_string: str,
                                /,
                                normalized_url: str,
                                gallery: GalleryUrl,
                                asset_count: int,
                                score: int,
                                created_at: datetime | str,
                                ) -> None:

    post_url_from_string: PostUrl = Url.parse(post_url_string)  # type: ignore[assignment]
    assert_post_url(post_url_from_string,
                    normalized_url=normalized_url,
                    gallery=gallery,
                    asset_count=asset_count,
                    score=score,
                    created_at=created_at,
                    check_from_string=False)


def assert_asset_url(asset_url: AssetUrl,
                     /,
                     normalized_url: str | None = None,
                     file_count: int = 1,
                     gallery: ArtistUrl | None = None,
                     created_at: datetime | str | None = None
                     ) -> AssetUrl:
    assert_is_instance(asset_url, AssetUrl)
    asset_url_from_string: AssetUrl = Url.parse(asset_url)  # type: ignore[assignment]

    assert_is_instance(asset_url_from_string, type(asset_url))

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
