import click

from danboorutools import logger
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.models.danbooru import DanbooruPostVersion
from danboorutools.util.threading import run_in_parallel

logger.log_to_file()


@click.command()
@click.argument("user_id", type=int, required=True)
@click.argument("tag", type=str, required=False)
def main(user_id: int, tag: str | None = None) -> None:
    nuke_tag_edits(user_id=user_id, tag=tag)


def nuke_tag_edits(user_id: int, tag: str | None) -> None:
    if not tag:
        raise NotImplementedError

    page = 1
    printed = False
    while True:
        logger.info(f"At page {page}...")
        versions = danbooru_api.post_versions(updater_id=user_id, added_tags_include_all=tag, page=page)
        if not versions:
            logger.info("Done!")
            return

        if not printed:
            logger.info(f"Nuking additions of '{tag}' by user {versions[0].updater.name}")
            printed = True

        assert all(version.updater.id == user_id for version in versions)
        run_in_parallel(_nuke_tag, versions, tag)

        page += 1


def _nuke_tag(version: DanbooruPostVersion, tag: str) -> None:
    if tag in version.post.tags:
        danbooru_api.update_post_tags(version.post, [f"-{tag}"])
