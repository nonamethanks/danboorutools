import click

from danboorutools import logger
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.models.danbooru import DanbooruPostVersion
from danboorutools.util.threading import run_in_parallel

logger.log_to_file()


@click.command()
@click.argument("user_id", type=int, required=True)
@click.argument("tag", type=str, required=False)
@click.option("--dry_run", "-d", is_flag=True, show_default=True, default=False)
def main(user_id: int, tag: str | None = None, dry_run: bool = False) -> None:
    logger.debug(f"UID: {user_id}, tag action: {tag}, dry run: {dry_run}")
    nuke_tag_edits(user_id=user_id, tag=tag, dry_run=dry_run)


def nuke_tag_edits(user_id: int, tag: str | None, dry_run: bool = False) -> None:
    if not tag:
        raise NotImplementedError

    page = 1
    printed = False

    was_removal = tag.startswith("-")
    tag = tag.removeprefix("-")
    search_key = "removed_tags_include_all" if was_removal else "added_tags_include_all"

    while True:
        logger.info(f"At page {page}...")

        arguments: dict = {
            "updater_id": user_id,
            "page": page,
            search_key: tag,
        }

        versions = danbooru_api.post_versions(**arguments)
        if not versions:
            logger.info("Done!")
            return

        if not printed:
            action_type = "removals" if was_removal else "additions"
            logger.info(f"Nuking {action_type} of '{tag}' by user {versions[0].updater.name}")
            printed = True

        assert all(version.updater.id == user_id for version in versions)
        if dry_run:
            continue

        run_in_parallel(_update_post, versions, tag, was_removal)  # type: ignore[arg-type]

        page += 1


def _update_post(version: DanbooruPostVersion, tag: str, was_removal: bool) -> None:
    if was_removal and tag not in version.post.tags:
        danbooru_api.update_post_tags(version.post, [tag])
    elif not was_removal and tag in version.post.tags:
        danbooru_api.update_post_tags(version.post, [f"-{tag}"])
