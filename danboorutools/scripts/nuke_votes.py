from pathlib import Path
from typing import TYPE_CHECKING

import click
from loguru import logger

from danboorutools.logical import danbooru_api

if TYPE_CHECKING:
    from danboorutools.models.danbooru import DanbooruCommentVote, DanbooruPostVote


logger.add(f"logs/scripts/{Path(__file__).stem}/" + "{time}.log", retention="7 days")


@click.command()
@click.argument("mode", type=click.Choice(["comments", "posts", "all"]))
@click.argument("user_ids", nargs=-1, required=True, type=int)
@click.confirmation_option(prompt="Are you sure?")
def main(mode: str, user_ids: list[int]) -> None:
    for user_id in user_ids:
        if mode == "posts":
            nuke_votes("post", user_id)
        elif mode == "comments":
            nuke_votes("comment", user_id)
        elif mode == "all":
            nuke_votes("post", user_id)
            nuke_votes("comment", user_id)


def nuke_votes(model: str, user_id: int) -> None:
    logger.info(f"Nuking {model} votes for user {user_id}...")
    count = 1
    while True:
        method = getattr(danbooru_api, f"{model}_votes")
        params = {"user": {"id": user_id}, "is_deleted": False}
        votes: list[DanbooruPostVote | DanbooruCommentVote] = method(**params)
        if not votes:
            return
        for vote in votes:
            assert vote.user.id == user_id  # sanity check
            logger.info(f"Nuking {model} vote for {model} {getattr(vote, model).url}. At vote {count}...")
            vote.delete()
            count += 1
