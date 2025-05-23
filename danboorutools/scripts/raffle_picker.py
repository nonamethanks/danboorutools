import random
from datetime import datetime
from pathlib import Path

import click

from danboorutools import logger, settings
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.models.danbooru import DanbooruForumPost, DanbooruPost, DanbooruUser

log_file = logger.log_to_file()

ARTIST_URLS_FILE = Path(settings.BASE_FOLDER / "data" / "artist_urls.txt")
SOURCE_URLS_FILE = Path(settings.BASE_FOLDER / "data" / "sources.txt")


@click.command()
@click.option("--topicid", type=int, required=True)
@click.option("--pick", type=int, default=0)
def main(topicid: int, pick: int) -> None:

    forum_posts = get_forum_posts(topic_id=topicid)

    forum_topic = forum_posts[0].topic
    assert forum_topic.created_at, forum_topic.updated_at

    uploads = get_uploads(start_time=forum_topic.created_at, end_time=forum_topic.updated_at)

    logger.info(f"{len(forum_posts)} forum posters collected.")
    forum_posters = list({post.creator.id: post.creator for post in forum_posts}.values())

    candidates = [Candidate(user=user) for user in forum_posters]
    logger.info(f"There are {len(candidates)} unique forum posters.")

    candidates = [candidate for candidate in candidates if candidate.user.level == 20]
    logger.info(f"Of these, {len(candidates)} are member-level.")

    candidates = [candidate for candidate in candidates if candidate.user.created_at < forum_topic.created_at]
    logger.info(f"Of these, {len(candidates)} are not new accounts.")

    upload_data: dict[int, list[DanbooruPost]] = {}
    for upload in uploads:
        try:
            upload_data[upload.uploader_id].append(upload)
        except KeyError:
            upload_data[upload.uploader_id] = [upload]

    for candidate in candidates:
        candidate.uploads = upload_data.get(candidate.user.id, [])
        candidate.uploaded_count = len([upload for upload in candidate.uploads if upload.uploader_id == candidate.user.id])
        candidate.approved_count = sum(upload.is_active for upload in candidate.uploads if upload.uploader_id == candidate.user.id)

    def upload_count(x: int) -> int:
        return len([c for c in candidates if c.uploaded_count >= x])

    logger.info(f"Of these, {upload_count(1)} have uploaded at least 1 post since the topic's creation.")
    logger.info(f"Of these, {upload_count(2)} have uploaded at least 2 posts since the topic's creation.")
    logger.info(f"Of these, {upload_count(10)} have uploaded at least 10 posts since the topic's creation.")
    logger.info(f"Of these, {upload_count(100)} have uploaded at least 100 posts since the topic's creation.")
    logger.info(
        f"In total, {sum(candidate.uploaded_count for candidate in candidates)} uploads were submitted during the entry period."
        f" {sum(candidate.approved_count for candidate in candidates)} were approved.")

    new_uploaders, newish_uploaders = [], []
    for c in candidates:
        if c.uploaded_count > 0 and c.uploaded_count == c.user.post_upload_count:
            new_uploaders += [c]
        elif c.uploaded_count > 0 and c.user.post_upload_count <= 10:
            newish_uploaders += [c]
    logger.info(f"In total, {len(new_uploaders)} are new uploaders, "
                f"and another {len(newish_uploaders)} had uploaded very few posts (<=10) posts before this.")

    logger.info("")
    logger.info("Top 10 uploaders:")
    for candidate in sorted(candidates, key=lambda c: c.uploaded_count, reverse=True)[:10]:
        logger.info(f"{candidate.user.url} {candidate.user.name} - {candidate.uploaded_count} posts, {candidate.approved_count} approved.")

    logger.info("")
    logger.info("")
    if not pick:
        return

    pickable = [p for c in candidates for p in [c]*(c.approved_count+1)]

    picked: list[Candidate] = []
    for _ in range(pick):
        while True:
            winner = random.choice(pickable)
            if winner.user.id not in [p.user.id for p in picked]:
                picked.append(winner)
                break

    logger.info("")
    logger.info("")
    logger.info("")
    logger.info("<r>Winners:</r>")
    for winner in sorted(picked, key=lambda c: c.user.id):
        logger.info(f"{winner.user.url} - {winner.user.name} - Uploaded {winner.uploaded_count} posts ({winner.approved_count} approved).")


def get_forum_posts(topic_id: int) -> list[DanbooruForumPost]:
    forum_posts: list[DanbooruForumPost] = []
    page = 1
    while True:
        logger.info(f"Collecting entries from topic #{topic_id}. At page {page}.")
        forum_posts += (_forum_posts := danbooru_api.forum_posts(topic_id=topic_id, page=page))
        if not _forum_posts:
            return forum_posts
        page += 1


def get_uploads(start_time: datetime, end_time: datetime) -> list[DanbooruPost]:
    logger.info("Collecting posts...")

    tags = [
        f"date:{danbooru_api.db_datetime(start_time)}..{danbooru_api.db_datetime(end_time)}",
        "(approver:any or status:pending or status:deleted)",
    ]

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


class Candidate:
    def __init__(self, user: DanbooruUser):
        self.user = user
        self.uploaded_count = 0
        self.approved_count = 0
        self.uploads: list[DanbooruPost] = []


# old raffle picker via nntbot dmail
#
#
#
# def old_raffle(start: str, count: int) -> None:
#     start_time = datetime_from_string(start)
#     end_time = start_time + timedelta(hours=24)
#
#     logger.info(f"Collecting posts between {start_time} and {end_time}.")
#
#     start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
#     end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
#
#     posts = get_uploads(start_time=start_time_str, end_time=end_time_str)
#
#     unique_uploaders = danbooru_api.users(id=",".join(map(str, {p.uploader_id for p in posts})))
#
#     users_that_sent_dmail = get_dmailers(start_time=start_time_str, end_time=end_time_str)
#
#     logger.info(f"There were {len(unique_uploaders)} unique uploaders.")
#     logger.info(f"There were {len(users_that_sent_dmail)} unique dmailers.")
#
#     sent_msg_and_uploaded = {user for user in unique_uploaders if user.id in users_that_sent_dmail}
#     logger.info(f"Of {len(users_that_sent_dmail)} dmailers, {len(sent_msg_and_uploaded)} uploaded at least one approved post.")
#
#     candidates = {user for user in sent_msg_and_uploaded if user.level == 20}
#     logger.info(f"Of these, {len(candidates)} are member-level.")
#
#     candidate_map = {u.id: u for u in candidates}
#     weighted = [candidate_map[post.uploader_id] for post in posts if post.uploader_id in candidate_map]
#     logger.info(f"Picking at random between {len(weighted)} posts...")
#     logger.info("Winners are:")
#
#     picked = 0
#     while picked < count:
#         winner = random.choice(weighted)
#         logger.info(f"{winner.name}, {winner.url}")
#         weighted = [u for u in weighted if u.id != winner.id]
#         picked += 1
#
#
# def get_uploads(start_time: str, end_time: str) -> list[DanbooruPost]:
#     logger.info("Collecting posts...")
#
#     tags = [f"date:{start_time}..{end_time}", "approver:any"]
#
#     posts: list[DanbooruPost] = []
#     page_number = 0
#     while True:
#         page_number += 1
#         logger.info(f"At page {page_number}")
#         page_of_posts = danbooru_api.posts(tags=tags, page=page_number)
#         if not page_of_posts:
#             logger.info(f"Collected {len(posts)} posts.")
#             return posts
#         posts += page_of_posts
#
#
# def get_dmailers(start_time: str, end_time: str) -> set[int]:
#     dmails = danbooru_api.dmails(created_at=f"{start_time}..{end_time}")
#     return {d.from_id for d in dmails}
