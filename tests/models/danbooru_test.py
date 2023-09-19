from ward import test

from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.models.danbooru import DanbooruPost, DanbooruUser


@test("Test fetching an user using danbooru", tags=["danbooru_api", "danbooru_users"])
def user_test() -> None:
    user, = danbooru_api.users(id=508240)
    test_admin_user(user)


@test("Test fetching an user using DanbooruUser", tags=["danbooru", "danbooru_users"])
def user_from_id_test() -> None:
    user = DanbooruUser.from_id(508240)
    test_admin_user(user)


def test_admin_user(user: DanbooruUser) -> None:
    assert user.id == 508240
    assert user.name == "nonamethanks"
    assert user.is_banned is False
    assert user.url == "https://danbooru.donmai.us/users/508240"
    assert user.post_update_count > 1_300_000
    assert user.post_upload_count > 80_000
    assert user.note_update_count > 10_000

    assert user.level == 50
    assert user.level_string == "Admin"


@test("Test fetching a post using danbooru_api", tags=["danbooru", "danbooru_posts"])
def post_test() -> None:
    post, = danbooru_api.posts(tags=["id:1"])
    test_post(post)


@test("Test fetching a post using DanbooruPost", tags=["danbooru", "danbooru_posts"])
def post_from_id_test() -> None:
    post = DanbooruPost.from_id(1)
    test_post(post)


def test_post(post: DanbooruPost) -> None:
    assert post.id == 1

    assert post.md5 == "d34e4cf0a437a5d65f8e82b7bcd02606"
    assert post.file_url == "https://cdn.donmai.us/original/d3/4e/d34e4cf0a437a5d65f8e82b7bcd02606.jpg"

    assert post.media_asset.image_height == 650
    assert post.media_asset.image_width == 459

    assert post.media_asset.file_ext == "jpg"

    assert post.media_asset.pixel_hash == "9c877dd5674d7fa251ce2de0c956fd36"
