from datetime import datetime

from danboorutools.models.url import ArtistUrl, AssetUrl, GalleryUrl, PostUrl, Url


def assert_parsed(string: str, url_type: type[Url], url_id: str | int | None = None) -> None:
    url = Url.parse(string)

    assert isinstance(url, url_type)
    assert url.id == str(url_id)


def assert_artist_url(url_string: str, /, is_deleted: bool, names: list[str], related: list[Url | str], post_count: int) -> ArtistUrl:
    artist_url = Url.parse(url_string)
    assert isinstance(artist_url, ArtistUrl)

    assert artist_url.is_deleted == is_deleted
    assert artist_url.names == names

    related_urls = [Url.parse(u) for u in related]
    assert sorted(related_urls, key=lambda u: u.normalized_url) == sorted(artist_url.related, key=lambda u: u.normalized_url)

    assert len(artist_url.posts) > post_count

    return artist_url


def assert_post_url(post_url: PostUrl, /,
                    normalized_url: str,
                    gallery: GalleryUrl,
                    asset_count: int,
                    score: int,
                    created_at: datetime
                    ) -> PostUrl:
    assert isinstance(post_url, PostUrl)
    post_url_from_string: PostUrl = Url.parse(post_url.normalized_url)  # type: ignore[assignment]

    assert isinstance(post_url_from_string, type(post_url))

    assert post_url.normalized_url == post_url_from_string.normalized_url == normalized_url

    assert post_url.gallery == post_url_from_string.gallery == gallery

    assert len(post_url.assets) == len(post_url_from_string.assets) == asset_count
    assert (post_url.score == post_url_from_string.score) > score

    assert post_url.created_at == post_url_from_string.created_at == created_at

    return post_url


def assert_asset_url(asset_url: AssetUrl, /,
                     normalized_url: str | None = None,
                     file_count: int = 1,
                     gallery: ArtistUrl | None = None,
                     created_at: datetime | None = None
                     ) -> AssetUrl:
    assert isinstance(asset_url, AssetUrl)
    asset_url_from_string = Url.parse(asset_url)

    assert isinstance(asset_url_from_string, type(asset_url))

    if normalized_url:
        assert asset_url.normalized_url == asset_url_from_string.normalized_url == normalized_url

    assert len(asset_url.files) == len(asset_url_from_string.files) == file_count

    if asset_url.post and asset_url_from_string.post:
        assert asset_url.post == asset_url_from_string.post

    if gallery:
        assert asset_url.post.gallery == asset_url_from_string.post.gallery == gallery

    if created_at:
        assert asset_url.created_at == asset_url_from_string.created_at == created_at

    return asset_url


def assert_asset_file(asset: AssetUrl, md5s: list[str]) -> None:
    files = asset.files
    assert sorted([f.md5 for f in files]) == sorted(md5s)

    for file in files:
        file.delete()
