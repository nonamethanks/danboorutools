from __future__ import annotations

import re
from typing import TYPE_CHECKING

from danboorutools import get_config, logger
from danboorutools.logical.sessions.danbooru import danbooru_api, testbooru_api
from danboorutools.util.misc import BaseModel

if TYPE_CHECKING:
    from danboorutools.models.danbooru import DanbooruTag

logger.log_to_file()

class Series(BaseModel):
    name: str
    topic_id: int

    @property
    def topic_url(self) -> str:
        return f"https://danbooru.donmai.us/forum_topics/{self.topic_id}"

config = get_config("auto_submit_implications.yaml")
series_list = [Series(**series) for series in config["series"]]


series_pattern = re.compile(r"(?P<base_name>.*)_(?P<costume_name>\(.*?\))_(?P<series>\(.*?\))")

bot_forum_posts = testbooru_api.forum_posts(body_matches="*Write a wiki page for them*", limit=1000, creator_name="nntbot")

def process_series(series: Series) -> None:
    logger.info(f"Processing series: {series.name}. Topic: {series.topic_url}")

    all_tags = collect_all_tags(series)
    costume_tags = list(filter(lambda tag: tag.name.endswith(f")_({series.name})"), all_tags))

    series_burs = testbooru_api.bulk_update_requests(script_ilike=f"*_({series.name})", limit=1000)
    if not series_burs:
        raise NotImplementedError

    tags_without_implications: list[DanbooruTag] = []

    for tag in costume_tags:
        for bur in series_burs:
            if f"{tag.name.lower()} ->" in bur.script.lower():
                logger.info(f"Skipping <c>{tag.name}</c> becasue it's already present in {bur.url}.")
                break
        else:
            tags_without_implications += [tag]

    logger.info("Tags without implications:")
    implications = []
    for subtag in sorted(tags_without_implications, key=lambda x: x.post_count, reverse=True):
        if (main_tag := process_tag(subtag, all_tags)):
            implications.append((subtag, main_tag))  # noqa: PERF401

    partitioned_implications: dict[DanbooruTag, list[DanbooruTag]] = {}
    for (subtag, main_tag) in implications:
        try:
            partitioned_implications[main_tag].append(subtag)
        except KeyError:
            partitioned_implications[main_tag] = [subtag]

    without_wiki = send_burs_and_return_without_wiki(series, partitioned_implications)
    post_tags_without_wikis(without_wiki, topic_id=series.topic_id)

def send_burs_and_return_without_wiki(series: Series, implications: dict[DanbooruTag, list[DanbooruTag]]) -> list:
    without_wiki: list[DanbooruTag] = []

    counter = 10
    script = ""

    for main_tag, subtags in implications.items():
        for tag in subtags:
            if tag._raw_data.get("wiki_page") is None:
                without_wiki.append(tag)
            else:
                script += f"imply {tag.name} -> {main_tag.name}\n"
                counter -= 1

        if counter <= 0:
            send_bur(series, script)
            script = ""
            counter = 10

    if script:
        send_bur(series, script)

    return without_wiki

def send_bur(series: Series, script: str) -> None:
    logger.info("Submitting implications:")
    logger.info(script)

    testbooru_api.create_bur(
        topic_id=series.topic_id,
        script=script,
        reason="beep boop. I found costume tags that needs an implications. Vote on it and say something if it's wrong.",
    )

def post_tags_without_wikis(tags: list[DanbooruTag], topic_id: int) -> None:

    missing_tags = [t for t in tags if not any(t.name in post.body for post in bot_forum_posts)]
    if missing_tags:
        logger.info(f"Posting tags without wiki pages: {', '.join(tag.name for tag in tags)}")
    else:
        logger.info("No tags without wiki pages to post.")
        return

    body = re.sub(r"\n +", "\n", f"""
        beep boop. I was going to submit an implication request for these tags, but they have no wiki page.
        Write a wiki page for them and I'll be able to do it next time I run.

        {'\n'.join(f"* [[{tag.name}]]" for tag in tags)}
    """)
    testbooru_api.create_forum_post(
        topic_id=topic_id,
        body=body,
    )

def collect_all_tags(series: Series) -> list[DanbooruTag]:
    tag_list = []
    page = 1
    while True:
        logger.info(f"Fetching all tags for {series.name} (page {page})...")
        results = testbooru_api.tags(
            name_matches=f"*_({series.name})",
            category=4,
            order="id",
            limit=1000,
            page=page,
            hide_empty=True,
        )
        tag_list += results
        if len(results) < 1000:
            logger.info(f"Finished fetching tags for {series.name}. Total: {len(tag_list)}")
            return tag_list
        page += 1

def process_tag(subtag: DanbooruTag, all_tags: list[DanbooruTag]) -> DanbooruTag | None:

    split_name = get_split_name(subtag.name)

    logger.info("")
    logger.info(f"Processing tag: {subtag.name}. Searching for potential tag: {split_name.base_tag}...")
    for tag in all_tags:
        if tag.name == split_name.base_tag:
            logger.info(f"Found potential implication <c>{tag.name} -> {subtag.name}.</c>")
            return tag

    logger.info(f"<red>No main tag found for {subtag.name}.</red>")
    return None

class SplitTagName(BaseModel):
    original: str

    base_name: str
    costume_name: str
    series: str

    @property
    def base_tag(self) -> str:
        return f"{self.base_name}_{self.series}"


def get_split_name(name: str) -> SplitTagName:
    # murasaki_shikibu_(swimsuit_rider)_(third_ascension)_(fate)
    # tezcatlipoca_(second_ascension)_(fate)
    # robin_(male)_(festive_tactician)_(fire_emblem)

    match = re.match(series_pattern, name)
    if not match:
        raise NotImplementedError(name)
    return SplitTagName(original=name, **match.groupdict())


def main() -> None:
    for series in series_list:
        process_series(series)


if __name__ == "__main__":
    main()
