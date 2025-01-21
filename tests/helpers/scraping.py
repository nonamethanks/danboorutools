from datetime import UTC, datetime
from typing import TypeVar

import pytest

from danboorutools.exceptions import DeadUrlError
from danboorutools.models.url import GalleryUrl, InfoUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.time import datetime_from_string

UrlTypeVar = TypeVar("UrlTypeVar", bound=Url)


class _TestUrl:
    url_string: str
    url_type: type[Url]
    url_properties: dict
    is_deleted: bool = False

    @pytest.fixture(scope="class")
    def parsed_url(self) -> Url:
        return Url.parse(self.url_string)

    @pytest.mark.parsing
    def test_correct_url_type(self, parsed_url: Url) -> None:
        expected_url_type = self.url_type
        assert isinstance(parsed_url, expected_url_type)

        # sanity check
        err_msg = "Dumbass, you configured the wrong type of test!"
        if isinstance(self, _TestRedirectUrl):
            assert isinstance(parsed_url, RedirectUrl), err_msg
        elif isinstance(self, _TestArtistUrl):
            assert isinstance(parsed_url, GalleryUrl), err_msg
        elif isinstance(self, _TestPostUrl):
            assert isinstance(parsed_url, PostUrl), err_msg
        elif isinstance(self, _TestInfoUrl):
            assert isinstance(parsed_url, InfoUrl), err_msg
        elif isinstance(self, _TestGalleryUrl):
            assert isinstance(parsed_url, GalleryUrl), err_msg

    @pytest.mark.parsing
    def test_correct_url_properties(self, parsed_url: Url) -> None:
        expected_properties = self.url_properties
        for property_name, expected_value in expected_properties.items():
            actual_value = getattr(parsed_url, property_name)
            assert actual_value == expected_value

    @pytest.mark.scraping
    def test_deleted_status(self, parsed_url: Url) -> None:
        expected_deleted = self.is_deleted
        assert parsed_url.is_deleted == expected_deleted


@pytest.mark.redirect
class _TestRedirectUrl(_TestUrl):
    redirects_to: str
    redirect_url_properties: dict | None = None

    @pytest.mark.scraping
    def test_redirect_to(self, parsed_url: RedirectUrl) -> None:
        try:
            expected_redirect = parsed_url.resolved.normalized_url
        except DeadUrlError:
            assert self.is_deleted
            return

        actual_redirect = Url.parse(self.redirects_to).normalized_url
        assert actual_redirect == expected_redirect

    @pytest.mark.scraping
    def test_redirect_url_properties(self, parsed_url: RedirectUrl) -> None:
        if self.redirect_url_properties is not None:
            resolved_url = parsed_url.resolved
            expected_properties = self.redirect_url_properties

            for property_name, expected_value in expected_properties.items():
                actual_value = getattr(resolved_url, property_name)
                assert actual_value == expected_value


class _TestInfoUrl(_TestUrl):
    primary_names: list[str]
    secondary_names: list[str]
    related: list[str]

    @pytest.mark.info
    @pytest.mark.scraping
    def test_primary_names(self, parsed_url: InfoUrl) -> None:
        expected_primary_names = self.primary_names
        actual_primary_names = parsed_url.primary_names
        assert sorted(actual_primary_names) == sorted(expected_primary_names)

    @pytest.mark.info
    @pytest.mark.scraping
    def test_secondary_names(self, parsed_url: InfoUrl) -> None:
        expected_secondary_names = self.secondary_names
        actual_secondary_names = parsed_url.secondary_names
        assert sorted(actual_secondary_names) == sorted(expected_secondary_names)

    @pytest.mark.info
    @pytest.mark.scraping
    def test_related(self, parsed_url: InfoUrl) -> None:
        expected_related = [Url.parse(u) for u in self.related]
        actual_related = parsed_url.related
        assert sorted(actual_related, key=lambda u: u.normalized_url) == sorted(expected_related, key=lambda u: u.normalized_url)


class _TestGalleryUrl(_TestInfoUrl):
    post_count: int | None = None
    posts: list[str] | None = None
    assets: list[str] | None = None

    @pytest.mark.gallery
    @pytest.mark.scraping
    def test_post_count(self, parsed_url: GalleryUrl) -> None:
        if self.post_count is not None:
            expected_post_count = self.post_count
            assert len(parsed_url.known_posts) >= expected_post_count

    @pytest.mark.gallery
    @pytest.mark.scraping
    def test_posts(self, parsed_url: GalleryUrl) -> None:
        if self.posts is not None:
            extracted_posts = parsed_url.extract_posts()
            expected_posts = [Url.parse(post) for post in self.posts]
            assert all(expected_post in extracted_posts for expected_post in expected_posts)

    @pytest.mark.gallery
    @pytest.mark.scraping
    def test_assets(self, parsed_url: GalleryUrl) -> None:
        if self.assets is not None:
            extracted_assets = parsed_url.assets
            expected_assets = [Url.parse(asset) for asset in self.assets]
            assert all(expected_asset in extracted_assets for expected_asset in expected_assets)


@pytest.mark.artist
class _TestArtistUrl(_TestGalleryUrl, _TestInfoUrl):
    ...


@pytest.mark.post
class _TestPostUrl(_TestUrl):
    created_at: datetime | str | None = None
    asset_count: int | None = None
    assets: list[str] | None = None
    score: int | None = None
    gallery: str | None = None

    @pytest.mark.scraping
    def test_created_at(self, parsed_url: PostUrl) -> None:
        if self.created_at is not None:
            expected_created_at = datetime_from_string(self.created_at).astimezone(UTC)
            actual_created_at = parsed_url.created_at.astimezone(UTC)
            assert actual_created_at == expected_created_at

    @pytest.mark.scraping
    def test_asset_count(self, parsed_url: PostUrl) -> None:
        if self.asset_count is not None:
            expected_asset_count = self.asset_count
            assert len(parsed_url.assets) >= expected_asset_count

    @pytest.mark.scraping
    def test_assets(self, parsed_url: PostUrl) -> None:
        if self.assets is not None:
            extracted_assets = parsed_url.assets
            expected_assets = [Url.parse(asset) for asset in self.assets]
            assert all(expected_asset in extracted_assets for expected_asset in expected_assets)

    @pytest.mark.scraping
    def test_score(self, parsed_url: PostUrl) -> None:
        if self.score is not None:
            expected_score = self.score
            actual_score = parsed_url.score
            assert actual_score >= expected_score

    @pytest.mark.scraping
    def test_gallery(self, parsed_url: PostUrl) -> None:
        if self.gallery is not None:
            actual_gallery = parsed_url.gallery
            expected_gallery = Url.parse(self.gallery)
            assert expected_gallery == actual_gallery
