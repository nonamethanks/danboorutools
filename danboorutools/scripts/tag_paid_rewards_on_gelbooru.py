import datetime
from pathlib import Path
from typing import Literal

import click

from danboorutools import logger
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.models.danbooru import DanbooruPost, DanbooruPostVersion
from danboorutools.models.gelbooru import GelbooruPost
from danboorutools.util.threading import Counter, run_in_parallel

logger.add(f"logs/scripts/{Path(__file__).stem}/" + "{time}.log", retention="7 days")


global_counter = Counter(print_progress=True)


@click.command()
@click.argument("mode", type=click.Choice(["all", "latest"]))
def main(mode: Literal["all"] | Literal["latest"]) -> None:
    tag_paid_rewards_on_gelbooru(mode)


def tag_paid_rewards_on_gelbooru(mode: Literal["all"] | Literal["latest"]) -> None:
    if mode == "all":
        posts = danbooru_api.all_posts(["paid_reward"])
    elif mode == "latest":
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        page = 1
        all_versions: list[DanbooruPostVersion] = []
        while True:
            found_versions = danbooru_api.post_versions(updated_at=f">{one_month_ago.isoformat()}",
                                                        added_tags_include_all="paid_reward",
                                                        page=page)
            if not found_versions:
                break
            all_versions += found_versions
            page += 1
        posts = list({
            post_version.post.id: post_version.post
            for post_version in all_versions
            if "paid_reward" in post_version.post.tags
        }.values())
    else:
        raise ValueError(mode)

    logger.info(f"Found {len(posts)} posts on danbooru tagged paid_reward. Sending the data to gelbooru...")

    run_in_parallel(tag_gelbooru_post, posts, global_counter)
    logger.info(f"Done! Tagged {global_counter} posts.")


def tag_gelbooru_post(post: DanbooruPost, counter: Counter = global_counter) -> None:
    gelbooru_post = GelbooruPost.from_md5(post.md5)
    if not gelbooru_post:
        return

    counter += bool(gelbooru_post.add_tags(["paid_reward"], send=True))
