from pathlib import Path

import click

from danboorutools import logger
from danboorutools.logical import danbooru_api
from danboorutools.logical.strategies import parse_url
from danboorutools.logical.strategies.ehentai import EHentaiGalleryUrl

logger.add(f"logs/scripts/{Path(__file__).stem}/" + "{time}.log", retention="7 days")


@click.command()
@click.argument("ehentai_url")
@click.argument("search_tags_str")
# I'm too lazy to make it work with >200 posts at once
def main(ehentai_url: str, search_tags_str: str) -> None:
    search_tags = search_tags_str.split(",")

    logger.info(f"Replacing the posts under {search_tags} with the gallery {ehentai_url}")

    parsed_url = parse_url(ehentai_url)
    if not isinstance(parsed_url, EHentaiGalleryUrl):
        raise ValueError("ehentai_url parameter must be a gallery link")

    posts = danbooru_api.posts(list(search_tags))
    if len(posts) == 200:
        raise NotImplementedError

    to_replace = [post for post in posts
                  if post.source.site_name == "ehentai"
                  and post.source.properties["gallery_id"] == parsed_url.properties["gallery_id"]]

    id_list = [p.id for p in to_replace]
    logger.info(f"These posts will be replaced: {danbooru_api.base_url}/posts?tags=id:{','.join(map(str, id_list))}")
    click.confirm("Continue?", abort=True)

    parsed_url.extract_posts()

    for post in posts:
        page, = [page for page in parsed_url.posts if page.normalized_url == post.source.normalized_url]
        asset, = page.assets
        post.replace(replacement_file=asset.file, final_source=page)

    logger.info("Done!")
