from ward import test

from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.models.danbooru import DanbooruPost, DanbooruUser


@test("Test fetching an user using danbooru", tags=["danbooru_api", "danbooru_users"])
def user_test() -> None:
    user, = danbooru_api.users(id=4)
    test_admin_user(user)


@test("Test fetching an user using DanbooruUser", tags=["danbooru", "danbooru_users"])
def user_from_id_test() -> None:
    user = DanbooruUser.from_id(4)
    test_admin_user(user)


def test_admin_user(user: DanbooruUser) -> None:
    assert user.id == 4
    assert user.name == "nonamethanks"
    assert user.is_banned is False
    assert user.url == "https://danbooru.donmai.us/users/4"
    assert 20 < user.post_update_count < 100
    assert 20 < user.post_upload_count < 100
    assert user.note_update_count == 1

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
