import time

import click

from danboorutools import logger
from danboorutools.logical.sessions.danbooru import danbooru_api

logger.log_to_file()


@click.command()
@click.argument("user_ids", nargs=-1, required=True, type=int)
@click.confirmation_option(prompt="Are you sure?")
def main(user_ids: list[int]) -> None:
    for user_id in user_ids:
        nuke_comments(user_id)


def nuke_comments(user_id: int) -> None:
    logger.info(f"Nuking comments for user https://danbooru.donmai.us/users/{user_id}...")
    count = 1
    while True:
        comments = danbooru_api.comments(is_deleted=False, creator_id=user_id)
        if not comments:
            return
        for comment in comments:
            assert comment.creator.id == user_id  # sanity check
            logger.info(f"Nuking comment #{comment.id}. At vote {count}...")
            comment.delete()
            time.sleep(0.3)
            count += 1
