from pathlib import Path

import click

from danboorutools import logger
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.logical.strategies.ehentai import EHentaiGalleryUrl, EHentaiPageUrl

logger.add(f"logs/scripts/{Path(__file__).stem}/" + "{time}.log", retention="7 days")


def main() -> None:
    while True:
        posts = danbooru_api.all_posts("source:*e-hentai* width:1280 age:<1mo".split())
        if not posts:
            logger.info("No galleries found!")
            return

        sources = [post.source for post in posts]
        gallery_ids = [source.id for source in sources]
        gallery_id_set = list(dict.fromkeys(gallery_ids))

        for index, gallery_id in enumerate(gallery_id_set):
            search_url = danbooru_api.url_for_search([f"source:*e*hentai.org/*{gallery_id}*"])
            logger.info(f"{index + 1}. {gallery_ids.count(gallery_id)} potential sample(s) for <c>{search_url}</c>")

        try:
            value = click.prompt("Which gallery to replace?", type=int)
        except click.exceptions.Abort:
            logger.info("Aborted!")
            return

        gallery_id = gallery_id_set[value - 1]
        page_url = [source for source in sources if isinstance(source, EHentaiPageUrl) and source.id == gallery_id][0]
        gallery_url = page_url.gallery

        search = f"source:*e*hentai.org/*{gallery_id}*"
        replace_from_gallery(gallery_url, search)


def replace_from_gallery(ehentai_url: EHentaiGalleryUrl, search_tags_str: str) -> None:
    search_tags = search_tags_str.split(",")

    logger.info(f"Replacing the posts under {search_tags} with the gallery {ehentai_url}")

    posts = danbooru_api.posts(list(search_tags))
    if len(posts) == 200:
        # I'm too lazy to make it work with >200 posts at once
        raise NotImplementedError

    id_list = [p.id for p in posts]
    logger.info(f"These posts will be replaced: {danbooru_api.base_url}/posts?tags=id:{','.join(map(str, id_list))}")
    click.confirm("Continue?", abort=True)

    if len(posts) > 5:
        extracted_pages = ehentai_url.posts
    else:
        extracted_pages: list[EHentaiPageUrl] = [post.source for post in posts]  # type: ignore[no-redef]
        for page in extracted_pages:
            assert isinstance(page, EHentaiPageUrl)

    for post in posts:
        page, = [page for page in extracted_pages if page.normalized_url == post.source.normalized_url]
        asset, = page.assets
        post.replace(replacement_file=asset.files[0], final_source=page)

    logger.info("Done!")
