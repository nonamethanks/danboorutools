import random
from datetime import datetime, timedelta
from pathlib import Path

import click

from danboorutools import logger, settings
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.models.danbooru import DanbooruPost
from danboorutools.util.time import datetime_from_string

log_file = logger.log_to_file()

ARTIST_URLS_FILE = Path(settings.BASE_FOLDER / "data" / "artist_urls.txt")
SOURCE_URLS_FILE = Path(settings.BASE_FOLDER / "data" / "sources.txt")


@click.command()
@click.option("--start", type=str, required=True)
@click.option("--count", type=int, default=10)
def main(start: str, count: int) -> None:
    start_time = datetime_from_string(start)
    end_time = start_time + timedelta(hours=24)

    logger.info(f"Collecting posts between {start_time} and {end_time}.")

    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    posts = get_uploads(start_time=start_time_str, end_time=end_time_str)

    unique_uploaders = danbooru_api.users(id=",".join(map(str, {p.uploader_id for p in posts})))

    users_that_sent_dmail = get_dmailers(start_time=start_time_str, end_time=end_time_str)

    logger.info(f"There were {len(unique_uploaders)} unique uploaders.")
    logger.info(f"There were {len(users_that_sent_dmail)} unique dmailers.")

    sent_msg_and_uploaded = {user for user in unique_uploaders if user.id in users_that_sent_dmail}
    logger.info(f"Of {len(users_that_sent_dmail)} dmailers, {len(sent_msg_and_uploaded)} uploaded at least one approved post.")

    candidates = {user for user in sent_msg_and_uploaded if user.level == 20}
    logger.info(f"Of these, {len(candidates)} are member-level.")

    candidate_map = {u.id: u for u in candidates}
    weighted = [candidate_map[post.uploader_id] for post in posts if post.uploader_id in candidate_map]
    logger.info(f"Picking at random between {len(weighted)} posts...")
    logger.info("Winners are:")

    picked = 0
    while picked < count:
        winner = random.choice(weighted)
        logger.info(f"{winner.name}, {winner.url}")
        weighted = [u for u in weighted if u.id != winner.id]
        picked += 1


def get_uploads(start_time: str, end_time: str) -> list[DanbooruPost]:
    logger.info("Collecting posts...")

    tags = [f"date:{start_time}..{end_time}", "approver:any"]

    posts: list[DanbooruPost] = []
    page_number = 0
    while True:
        page_number += 1
        logger.info(f"At page {page_number}")
        page_of_posts = danbooru_api.posts(tags=tags, page=page_number)
        if not page_of_posts:
            logger.info(f"Collected {len(posts)} posts.")
            return posts
        posts += page_of_posts


def get_dmailers(start_time: str, end_time: str) -> set[int]:
    dmails = danbooru_api.dmails(created_at=f"{start_time}..{end_time}")
    return {d.from_id for d in dmails}
