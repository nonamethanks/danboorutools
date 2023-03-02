import click

from danboorutools import logger
from danboorutools.logical.artist_finder import ArtistFinder
from danboorutools.logical.sessions.danbooru import danbooru_api

logger.log_to_file()


@click.command()
@click.argument("search", type=str, nargs=-1, required=True)
def main(search: tuple[str, ...]) -> None:
    add_artists_to_posts(list(search))


def add_artists_to_posts(search: list[str]) -> None:
    artist_post_tagger = ArtistFinder()

    search = list(set(search + "arttags:0 -anime_screencap -third-party_edit -third-party_source -second-party_source".split()))
    if not any(t.startswith("limit:") for t in search):
        search += ["limit:20"]
    page = "1"
    while True:
        posts = danbooru_api.posts(search, page=page)  # todo: create paginate generator that loops through 1M IDs to avoid timeouts
        if not posts:
            logger.info("Done!")
        page = f"b{posts[-1].id}"

        for post in posts:
            artist_post_tagger.create_or_tag_artist_for_post(post)
