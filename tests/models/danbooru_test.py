import pytest

from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.models.danbooru import DanbooruPost, DanbooruUser


@pytest.mark.danbooru
@pytest.mark.scraping
def test_user_test() -> None:
    user, = danbooru_api.users(id=508240)
    admin_user_t(user)


@pytest.mark.danbooru
@pytest.mark.scraping
def test_user_from_id_test() -> None:
    user = DanbooruUser.from_id(508240)
    admin_user_t(user)


def admin_user_t(user: DanbooruUser) -> None:
    assert user.id == 508240
    assert user.name == "nonamethanks"
    assert user.is_banned is False
    assert user.url == "https://danbooru.donmai.us/users/508240"
    assert user.post_update_count > 1_300_000
    assert user.post_upload_count > 80_000
    assert user.note_update_count > 10_000

    assert user.level == 50
    assert user.level_string == "Admin"


@pytest.mark.danbooru
@pytest.mark.scraping
def post_test() -> None:
    post, = danbooru_api.posts(tags=["id:1"])
    post_t(post)


@pytest.mark.danbooru
@pytest.mark.scraping
def post_from_id_test() -> None:
    post = DanbooruPost.from_id(1)
    post_t(post)


def post_t(post: DanbooruPost) -> None:
    assert post.id == 1

    assert post.md5 == "d34e4cf0a437a5d65f8e82b7bcd02606"
    assert post.file_url == "https://cdn.donmai.us/original/d3/4e/d34e4cf0a437a5d65f8e82b7bcd02606.jpg"

    assert post.media_asset.image_height == 650
    assert post.media_asset.image_width == 459

    assert post.media_asset.file_ext == "jpg"

    assert post.media_asset.pixel_hash == "9c877dd5674d7fa251ce2de0c956fd36"
