from __future__ import annotations

import ast
import re
from functools import cached_property
from itertools import groupby

from danboorutools import get_config, logger
from danboorutools.logical.sessions.danbooru import danbooru_api, testbooru_api
from danboorutools.models.danbooru import DanbooruBulkUpdateRequest, DanbooruTag  # noqa: TC001
from danboorutools.util.misc import BaseModel

PROD = False
db_api = danbooru_api if PROD else testbooru_api

logger.log_to_file()


class Series(BaseModel):
    name: str
    topic_id: int

    costume_patterns: list[re.Pattern]

    @property
    def topic_url(self) -> str:
        return f"https://danbooru.donmai.us/forum_topics/{self.topic_id}"

    @cached_property
    def all_tags(self) -> list[DanbooruTag]:
        tag_list = []
        page = 1
        while True:
            logger.info(f"Fetching all tags for {self.name} (page {page})...")
            results = db_api.tags(
                name_matches=f"*_({self.name})",
                category=4,
                order="id",
                limit=1000,
                page=page,
                hide_empty=True,
            )
            tag_list += results
            if len(results) < 1000:
                logger.info(f"Finished fetching tags for {self.name}. Total: {len(tag_list)}")
                return tag_list
            page += 1

    @cached_property
    def costume_tags(self) -> list[DanbooruTag]:
        return list(filter(lambda tag: any(p.match(tag.name) for p in self.costume_patterns), self.all_tags))

    @cached_property
    def burs(self) -> list[DanbooruBulkUpdateRequest]:
        series_burs = db_api.bulk_update_requests(script_ilike=f"*_({self.name})*", limit=1000)
        if not series_burs:
            raise NotImplementedError
        return series_burs

    @cached_property
    def tags_without_implications(self) -> list[DanbooruTag]:
        tags_without_implications = [
            tag for tag in self.costume_tags
            if not any(f"imply {tag.name.lower()} ->" in bur.script.lower() for bur in self.burs)
            and not any(f"create implication {tag.name.lower()} ->" in bur.script.lower() for bur in self.burs)
        ]
        logger.info(f"Found <r>{len(tags_without_implications)}</r> tags without an implication BUR.")
        return tags_without_implications

    def get_base_tag_name(self, name: str) -> str:
        # murasaki_shikibu_(swimsuit_rider)_(third_ascension)_(fate)
        # tezcatlipoca_(second_ascension)_(fate)
        # robin_(male)_(festive_tactician)_(fire_emblem)

        for pattern in self.costume_patterns:
            if (match := pattern.match(name)):
                return "{base_name}_{series_name}".format(**match.groupdict())

        raise NotImplementedError(name)

    def search_for_main_tag(self, subtag: DanbooruTag) -> DanbooruTag | None:
        base_tag = self.get_base_tag_name(subtag.name)

        logger.debug("")
        logger.debug(f"Processing tag: <g>{subtag.name}</g>. Searching for potential tag: <g>{base_tag}</g>...")
        for candidate in self.all_tags:
            if candidate.name == base_tag:
                logger.debug(f"Found potential implication <g>{subtag.name} -> {candidate.name}.</g>")
                return candidate

        logger.debug(f"<red>No main tag found for {subtag.name}.</red>")
        return None

    @property
    def implication_groups(self) -> list[ImplicationGroup]:
        return [
            ImplicationGroup(main_tag=main_tag, subtags=list(subtags), series=self)
            for main_tag, subtags in groupby(self.tags_without_implications, key=lambda tag: self.search_for_main_tag(tag))
            if main_tag
        ]


class ImplicationGroup(BaseModel):
    main_tag: DanbooruTag
    subtags: list[DanbooruTag]

    series: Series

    @property
    def script(self) -> str:
        return "\n".join(f"imply {subtag.name} -> {self.main_tag.name}" for subtag in self.subtags)

    @property
    def tags_without_wiki(self) -> list[DanbooruTag]:
        return [tag for tag in self.subtags if tag._raw_data.get("wiki_page") is None]

    def create_missing_wikis(self) -> None:
        for tag in self.tags_without_wiki:
            logger.info(f"Creating wiki page for {tag.name} {tag.url}")
            db_api.create_wiki_page(title=tag.name, body=self.wiki_template)

    @property
    def wiki_template(self) -> str:
        body = f"""
        Alternate costume for [[{self.main_tag.name}]].

        h4. Appearance
        * !post #REPLACEME
        """

        return re.sub(r"\n +", "\n", body)


bot_forum_posts = db_api.forum_posts(body_matches="*Write a wiki page for them*", limit=1000, creator_name="nntbot")


def process_series(series: Series) -> None:
    logger.info(f"Processing series: {series.name}. Topic: {series.topic_url}")

    counter = 10
    script = ""

    for group in series.implication_groups:
        logger.info(f"Found implication group: {group.main_tag.name} -> {", ".join(tag.name for tag in group.subtags)}")
        group.create_missing_wikis()

        counter -= len(group.subtags)
        script += group.script + "\n"

        if counter <= 0:
            send_bur(series, script)
            script = ""
            counter = 10

    if script:
        send_bur(series, script)


def send_bur(series: Series, script: str) -> None:
    logger.info("Submitting implications:")
    logger.info(script)

    db_api.create_bur(
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
    db_api.create_forum_post(
        topic_id=topic_id,
        body=body,
    )


def main() -> None:
    config = get_config("auto_submit_implications.yaml")

    default_pattern = re.compile(r"(?P<base_name>.*)_(?P<costume_name>\(.*?\))_(?P<series_name>\(.*?\))")

    series_list = [
        Series(**series | {
            "costume_patterns": [ast.literal_eval(p) for p in series["costume_patterns"]] + [default_pattern],
        })
        for series in config["series"]
    ]

    for series in series_list:
        process_series(series)


if __name__ == "__main__":
    main()
