
from __future__ import annotations

from datetime import timedelta
from itertools import batched
from typing import TYPE_CHECKING

import click

from danboorutools import logger
from danboorutools.logical.sessions.danbooru import danbooru_api

if TYPE_CHECKING:
    from datetime import datetime

    from danboorutools.models.danbooru import DanbooruAppeal, DanbooruFlag

logger.log_to_file()


@click.command()
@click.option("--sinceid", type=int, default=0)
@click.option("--maxid", type=int, default=0)
def main(sinceid: int, maxid: int) -> None:
    maxid = maxid or sinceid

    reference_post, = danbooru_api.posts(tags=[f"id:{sinceid}"])
    since = reference_post.created_at

    flags = collect_flags(since=since)
    logger.info(f"{"#"*40} FLAGS {"#"*40}")
    flags = [f for f in flags if f.post.id < maxid]
    for chunk in batched(flags, 500):
        logger.info(f"https://danbooru.donmai.us/posts?tags=-status:active+id:{",".join(str(flag.post.id) for flag in chunk)}")

    appeals = collect_appeals(since=since)
    appeals = [a for a in appeals if a.created_at > a.post.created_at + timedelta(days=7) and a.post.id < maxid]
    logger.info(f"{"#"*40} APPEALS {"#"*40}")
    for chunk in batched(appeals, 500):
        logger.info(f"https://danbooru.donmai.us/posts?tags=-status:active+id:{",".join(str(appeal.post.id) for appeal in chunk)}")


def collect_flags(since: datetime) -> list[DanbooruFlag]:

    flags = []

    logger.info("Collecting flags...")
    page = 1

    while True:
        _flags = danbooru_api.flags(
            created_at=f">{since.isoformat()}",
            category="normal",
            **{"search[post][is_deleted]": True},
            page=page,
        )

        if not _flags:
            return flags

        page += 1
        flags += _flags


def collect_appeals(since: datetime) -> list[DanbooruAppeal]:
    appeals = []
    page = 1

    while True:
        _appeals = danbooru_api.appeals(
            created_at=f">{since.isoformat()}",
            page=page,
        )

        if not _appeals:
            return appeals

        page += 1
        appeals += _appeals
