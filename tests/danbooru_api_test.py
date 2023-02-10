import random

from ward import test

from danboorutools.logical.sessions.danbooru import danbooru_api, kwargs_to_include


@test("Test the parsing of kwargs", tags=["parsing"])
def test_kwargs_parsing() -> None:
    kwargs = {
        "id": 508240
    }
    assert kwargs_to_include(**kwargs) == {"search[id]": 508240}


@test("Test the parsing of complex kwargs", tags=["parsing"])
def test_kwargs_nested_parsing() -> None:
    kwargs = {
        "A": "b",
        "c": {
            "d": "e",
            "e": "f",
            "g": {
                "h": "i",
                "j": "k"
            }
        },
        "page": 1,
        "order": "id",
        "limit": 20,
        "only": "1,2,3"
    }

    expected = {
        "search[A]": "b",
        "search[c][d]": "e",
        "search[c][e]": "f",
        "search[c][g][h]": "i",
        "search[c][g][j]": "k",
        "search[order]": "id",
        "limit": 20,
        "page": 1,
        "only": "1,2,3"
    }

    assert kwargs_to_include(**kwargs) == expected


@test("Test the users.json endpoint", tags=["danbooru", "danbooru_users"])
def test_users() -> None:
    users = danbooru_api.users(limit=100)
    assert len(users) == 100

    user = random.choice(users[1:-2])
    assert users[users.index(user) + 1].id + 1 == user.id
    assert users[users.index(user) - 1].id - 1 == user.id


@test("Test the post_votes.json endpoint", tags=["danbooru", "danbooru_posts"])
def test_post_votes() -> None:
    post_votes = danbooru_api.post_votes(limit=100)
    assert len(post_votes) == 100

    post_vote = random.choice(post_votes[1:-2])
    assert post_votes[post_votes.index(post_vote) + 1].id + 1 == post_vote.id
    assert post_votes[post_votes.index(post_vote) - 1].id - 1 == post_vote.id


@test("Test the comment_votes.json endpoint", tags=["danbooru", "danbooru_comments"])
def test_comment_votes() -> None:
    comment_votes = danbooru_api.comment_votes(limit=100)
    assert len(comment_votes) == 100

    comment_vote = random.choice(comment_votes[1:-2])
    assert comment_votes[comment_votes.index(comment_vote) + 1].id + 1 == comment_vote.id
    assert comment_votes[comment_votes.index(comment_vote) - 1].id - 1 == comment_vote.id
