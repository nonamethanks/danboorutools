import re
from datetime import datetime
from typing import Callable, Generic, NotRequired, TypedDict, TypeVar, Unpack

from danboorutools.logical.parsers import UrlParser
from danboorutools.models.url import ArtistUrl, GalleryUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from tests import assert_comparison, assert_equal


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

###########################################################


class UrlTestKwargs(TypedDict, Generic[UrlTypeVar]):
    url: str | re.Pattern[str]
    url_type: type[UrlTypeVar]
    url_properties: dict[str, str | int]
    normalized_url: NotRequired[str]


class PostAssetTestKwargs(UrlTestKwargs[PostAssetUrlTypeVar]):
    file_md5: str
    post: NotRequired[PostUrl]
    file_count: NotRequired[int]
    created_at: NotRequired[datetime | str]


class PostTestKwargs(UrlTestKwargs[PostUrlTypeVar]):
    gallery: NotRequired[GalleryUrl]
    score: int
    asset_count: int
    created_at: datetime | str

    asset: NotRequired[PostAssetTestKwargs]


class GalleryTestKwargs(UrlTestKwargs[GalleryUrlTypeVar]):
    post_count: int
    is_deleted: NotRequired[bool]
    post: NotRequired[PostTestKwargs]


class InfoTestKwargs(UrlTestKwargs[InfoUrlTypeVar]):
    names: list[str]
    related: list[str]


class ArtistTestKwargs(InfoTestKwargs[ArtistUrlTypeVar], GalleryTestKwargs[ArtistUrlTypeVar]):  # type: ignore[misc]
    ...

###########################################################


def assert_gallery_url(**kwargs: Unpack[GalleryTestKwargs[GalleryUrlTypeVar]]) -> GalleryUrlTypeVar:
    assert isinstance(kwargs["url"], str)
    gallery = assert_casted(kwargs["url"], kwargs["url_type"])
    for key, value in kwargs["url_properties"].items():
        assert_equal(getattr(gallery, key), value)

    if kwargs.get("normalized_url"):
        assert_equal(gallery.normalized_url, kwargs["normalized_url"])
    elif isinstance(gallery, str):
        assert_equal(gallery.normalized_url, gallery)

    assert_equal(gallery.is_deleted, kwargs.get("is_deleted", False))

    assert_comparison(gallery.posts, ">=", kwargs["post_count"])

    return gallery


def assert_artist_url(**kwargs: Unpack[ArtistTestKwargs[ArtistUrlTypeVar]]) -> ArtistUrlTypeVar:
    gallery_data: GalleryTestKwargs[ArtistUrlTypeVar] = {
        "url": kwargs["url"],
        "url_type": kwargs["url_type"],
        "url_properties": kwargs["url_properties"],
        "post_count": kwargs["post_count"],
    }

    artist = assert_gallery_url(**gallery_data)

    assert_equal(sorted(artist.primary_names), sorted(kwargs["names"]))
    assert_urls_are_same(kwargs["related"], artist.related)

    return artist


def assert_post_url(**kwargs: Unpack[PostTestKwargs[PostUrlTypeVar]]) -> PostUrl:
    assert isinstance(kwargs["url"], str)
    post = assert_casted(kwargs["url"], kwargs["url_type"])
    for key, value in kwargs["url_properties"].items():
        assert_equal(getattr(post, key), value)

    if kwargs.get("normalized_url"):
        assert_equal(post.normalized_url, kwargs["normalized_url"])
    else:
        assert_equal(post.normalized_url, kwargs["url"])
    if kwargs.get("gallery"):
        assert_equal(post.gallery, kwargs["gallery"])

    assert_equal(post.created_at, kwargs["created_at"])
    assert_equal(len(post.assets), kwargs["asset_count"])
    assert_comparison(post.score, ">=", kwargs["score"])

    return post


def assert_asset_url(**kwargs: Unpack[PostAssetTestKwargs[PostAssetUrlTypeVar]]) -> PostAssetUrl:
    assert isinstance(kwargs["url"], str)
    asset = assert_casted(kwargs["url"], kwargs["url_type"])

    for key, value in kwargs["url_properties"].items():
        assert_equal(getattr(asset, key), value)

    if kwargs.get("normalized_url"):
        assert_equal(asset.normalized_url, kwargs["normalized_url"])

    if kwargs.get("post"):
        assert_equal(kwargs["post"], asset.post)

    assert_equal(len(asset.files), kwargs.get("file_count", 1))

    if kwargs.get("created_at"):
        assert_equal(asset.created_at, kwargs["created_at"])

    if kwargs.get("file_md5"):
        md5s = [_file.md5 for _file in asset.files]
        assert kwargs["file_md5"] in md5s

    return asset


def assert_asset_file(asset: PostAssetUrl, md5s: list[str]) -> None:
    files = asset.files
    assert_equal(sorted([f.md5 for f in files]), sorted(md5s))

    for file in files:
        file.delete()


def assert_info_url(info_url: Url | str, related: list[Url] | list[str], names: list[str]) -> InfoUrl:
    info_url = assert_casted(info_url, InfoUrl)

    assert_urls_are_same(info_url.related, related)
    assert_equal(sorted(info_url.primary_names), sorted(names))

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


def generate_gallery_test_suite(**kwargs: Unpack[GalleryTestKwargs[GalleryUrlTypeVar]]) -> dict:
    assert isinstance(kwargs["url"], str)

    def _run_gallery_test() -> None:
        _gallery = assert_gallery_url(**kwargs)
        if kwargs["post"]:
            if isinstance(kwargs["post"]["url"], str):
                assert any(post for post in _gallery.posts if post.normalized_url == kwargs["post"]["url"])
            else:
                _post, = [post for post in _gallery.posts if kwargs["post"]["url"].search(post.normalized_url)]
                post = kwargs["post"].copy()
                post["url"] = _post.normalized_url
                assert_post_url(**post)

    tests = {"gallery": _run_gallery_test}

    if (post := kwargs["post"]) and isinstance(post["url"], str):  # type: ignore[redundant-expr] # false positive
        gallery = assert_casted(kwargs["url"], kwargs["url_type"])
        post["gallery"] = gallery
        tests |= generate_post_test_suite(**post)

    return tests


def generate_artist_test_suite(**kwargs: Unpack[ArtistTestKwargs[ArtistUrlTypeVar]]) -> dict:
    assert isinstance(kwargs["url"], str)

    def _run_artist_test() -> None:
        _artist = assert_artist_url(**kwargs)
        if kwargs["post"]:
            if isinstance(kwargs["post"]["url"], str):
                assert any(post for post in _artist.posts if post.normalized_url == kwargs["post"]["url"])
            else:
                _post, = [post for post in _artist.posts if kwargs["post"]["url"].search(post.normalized_url)]
                post = kwargs["post"].copy()
                post["url"] = _post.normalized_url
                assert_post_url(**post)

    tests = {"artist": _run_artist_test}

    if (post := kwargs["post"]) and isinstance(post["url"], str):  # type: ignore[redundant-expr] # false positive
        artist = assert_casted(kwargs["url"], kwargs["url_type"])
        post["gallery"] = artist
        tests |= generate_post_test_suite(**post)

    return tests


def generate_post_test_suite(**kwargs: Unpack[PostTestKwargs[PostUrlTypeVar]]) -> dict:
    assert isinstance(kwargs["url"], str)

    def _run_post_test() -> None:
        _post = assert_post_url(**kwargs)
        if kwargs["asset"]:
            if isinstance(kwargs["asset"]["url"], str):
                assert any(asset for asset in _post.assets if asset.normalized_url == kwargs["asset"]["url"])
            else:
                _asset, = [asset for asset in _post.assets if kwargs["asset"]["url"].search(asset.normalized_url)]
                asset = kwargs["asset"].copy()
                asset["url"] = _asset.normalized_url
                assert_asset_url(**asset)

    tests = {"post": _run_post_test}
    if (asset := kwargs["asset"]) and isinstance(asset["url"], str):  # type: ignore[redundant-expr] # false positive
        post = assert_casted(kwargs["url"], kwargs["url_type"])
        asset["post"] = post
        tests |= generate_asset_test_suite(**asset)

    return tests


def generate_asset_test_suite(**kwargs: Unpack[PostAssetTestKwargs[PostAssetUrlTypeVar]]) -> dict:
    assert isinstance(kwargs["url"], str)

    def _run_asset_test() -> None:
        assert_asset_url(**kwargs)

    tests = {"asset": _run_asset_test}

    return tests
