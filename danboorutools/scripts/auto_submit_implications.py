from __future__ import annotations

import ast
import os
import re
from datetime import UTC, datetime, timedelta
from functools import cached_property
from itertools import batched, groupby

from danboorutools import get_bool_env, get_config, logger
from danboorutools.logical.sessions.danbooru import danbooru_api, kwargs_to_include
from danboorutools.models.danbooru import DanbooruBulkUpdateRequest  # noqa: TC001
from danboorutools.util.misc import BaseModel, remove_indent

logger.log_to_file()

if (POST_TO_PROD := get_bool_env("AUTO_IMPLICATIONS_ENABLED")):
    logger.info("<r>PROD MODE for implications is enabled. The implications WILL be posted.</r>")
else:
    logger.info("<g>PROD MODE for implications is disabled. Nothing will be posted to the site.</g>")


class DanbooruImplicationData(BaseModel):
    antecedent_name: str
    consequent_name: str


class DanbooruTagData(BaseModel):
    name: str
    id: int
    antecedent_implications: list[DanbooruImplicationData]
    wiki_page: dict | None = None


class Series(BaseModel):
    name: str
    topic_id: int

    costume_patterns: list[re.Pattern]

    @property
    def topic_url(self) -> str:
        return f"https://danbooru.donmai.us/forum_topics/{self.topic_id}"

    @cached_property
    def burs(self) -> list[DanbooruBulkUpdateRequest]:
        series_burs = danbooru_api.bulk_update_requests(script_ilike=f"*_({self.name})*", limit=1000)
        if not series_burs:
            raise NotImplementedError
        return series_burs

    @cached_property
    def all_tags(self) -> list[DanbooruTagData]:
        tag_list = []
        page = 1
        while True:
            logger.info(f"Fetching all tags for {self.name} (page {page})...")

            results = danbooru_api.danbooru_request(
                "GET",
                "tags.json",
                params=kwargs_to_include(
                    name_matches=f"*_({self.name})",
                    category=4,
                    order="id",
                    limit=1000,
                    page=page,
                    hide_empty=True,
                    only="id,name,antecedent_implications,wiki_page",
                ))
            tag_list += [DanbooruTagData(**r) for r in results]
            if len(results) < 1000:
                logger.info(f"Finished fetching tags for {self.name}. Total: {len(tag_list)}")
                return tag_list
            page += 1

    @cached_property
    def costume_tags(self) -> list[DanbooruTagData]:
        return list(filter(lambda tag: any(p.match(tag.name) for p in self.costume_patterns), self.all_tags))

    @cached_property
    def tags_without_implications(self) -> list[DanbooruTagData]:
        tags_without_implications = [
            tag for tag in self.costume_tags
            if not tag.antecedent_implications
            and not any(f"imply {tag.name.lower()} ->" in bur.script.lower() for bur in self.burs)
            and not any(f"create implication {tag.name.lower()} ->" in bur.script.lower() for bur in self.burs)
        ]
        logger.info(f"Found <r>{len(tags_without_implications)}</r> tags without an implication (pending or otherwise).")
        return tags_without_implications

    def get_base_tag_name(self, name: str) -> str:
        # murasaki_shikibu_(swimsuit_rider)_(third_ascension)_(fate)
        # tezcatlipoca_(second_ascension)_(fate)
        # robin_(male)_(festive_tactician)_(fire_emblem)

        for pattern in self.costume_patterns:
            if (match := pattern.match(name)):
                return "{base_name}_{series_name}".format(**match.groupdict())

        raise NotImplementedError(name)

    def search_for_main_tag(self, subtag: DanbooruTagData) -> DanbooruTagData | None:
        base_tag = self.get_base_tag_name(subtag.name)
        for candidate in self.all_tags:
            if candidate.name == base_tag:
                return candidate

        return None

    @property
    def implication_groups(self) -> list[ImplicationGroup]:
        return sorted(
            [ImplicationGroup(main_tag=main_tag, subtags=list(subtags), series=self)
             for main_tag, subtags in groupby(self.tags_without_implications, key=lambda tag: self.search_for_main_tag(tag))
             if main_tag],
            key=lambda i: i.main_tag.name,
        )


class ImplicationGroup(BaseModel):
    main_tag: DanbooruTagData
    subtags: list[DanbooruTagData]

    series: Series

    @property
    def script(self) -> str:
        return "\n".join(f"imply {subtag.name} -> {self.main_tag.name}" for subtag in self.tags_with_wiki)

    @property
    def tags_with_wiki(self) -> list[DanbooruTagData]:
        return [tag for tag in self.subtags if tag.wiki_page]

    @property
    def tags_without_wiki(self) -> list[DanbooruTagData]:
        return [tag for tag in self.subtags if not tag.wiki_page]

    # def create_missing_wikis(self) -> None:
    #     for tag in self.tags_without_wiki:
    #         logger.info(f"Creating wiki page for {tag.name} {tag.url}")
    #         db_api.create_wiki_page(title=tag.name, body=self.wiki_template)

    # @property
    # def wiki_template(self) -> str:
    #     body = f"""
    #     Alternate costume for [[{self.main_tag.name}]].
    #
    #     h4. Appearance
    #     * !post #REPLACEME
    #     """
    #
    #     return remove_indent(body)


POSTED_THRESHOLD = datetime.now(UTC) - timedelta(weeks=2)
bot_username = os.environ["DANBOORU_BOT_USERNAME"]
bot_forum_posts = danbooru_api.forum_posts(
    body_matches="*Write a wiki page for them*",
    limit=1000,
    creator_name=bot_username,
    created_at=f">{danbooru_api.db_datetime(POSTED_THRESHOLD)}",
)

IMPLICATIONS_PER_BULK = 10


def process_series(series: Series) -> None:
    bulk_mode = len(series.implication_groups) > 5
    logger.info(f"Processing series: {series.name}. Topic: {series.topic_url}.")
    logger.info(f"There are {len(series.implication_groups)} implication groups. Bulk mode: {bulk_mode}")

    counter = IMPLICATIONS_PER_BULK
    script = ""
    tags_with_no_wikis = []

    for group in series.implication_groups:
        logger.info(f"Found implication group: {", ".join(tag.name for tag in group.subtags)} -> {group.main_tag.name} ")
        if group.tags_without_wiki:
            logger.info(f"There are {len(group.tags_without_wiki)} tags without a wiki.")
            tags_with_no_wikis += group.tags_without_wiki

        if not group.tags_with_wiki:
            logger.info("<r>This group has no remaining tags with wiki. Moving on...</r>")
            continue

        if bulk_mode:
            counter -= len(group.tags_with_wiki)
            script += group.script + "\n"

            if counter <= 0:
                send_bur(series, script)
                script = ""
                counter = 10
        else:
            send_bur(series, group.script)

    if script:
        send_bur(series, script)

    post_tags_without_wikis(tags_with_no_wikis, series.topic_id)


def send_bur(series: Series, script: str) -> None:
    logger.info("Submitting implications:")
    logger.info(f"\n<c>{script}</c>")
    bur_reason = """
        beep boop. I found costume tags that needs an implications. Vote on this BUR and say something if you disagree.

        [tn]This is an automatic post. Use topic #31779 to report errors/false positives or general feedback.[/tn]
    """

    if POST_TO_PROD:
        danbooru_api.create_bur(
            topic_id=series.topic_id,
            script=script,
            reason=bur_reason,
        )


def post_tags_without_wikis(tags: list[DanbooruTagData], topic_id: int) -> None:
    unposted = [t for t in tags if not any(f"[[{t.name}]]" in post.body for post in bot_forum_posts)]
    if unposted:
        logger.info(f"Posting tags without wiki pages: {', '.join(tag.name for tag in tags)}")
    else:
        logger.info("No tags without wiki pages to post.")
        return

    body = """
        beep boop. I was going to submit an implication request for these tags, but they have no wiki page.
        Write a wiki page for them and I'll be able to do it next time I run.
    """

    if len(unposted) > 10:
        body += "\n[expand Tags without a wiki]"
    for tag in unposted:
        body += f"\n* [[{tag.name}]]"
    if len(unposted) > 10:
        body += "\n[/expand]"

    body += """

        Self-updating links to all tags without wiki from this series:
    """
    for index, tag_batch in enumerate(batched(tags, 100)):
        body += f'\n"Link #{index+1}":/tags?search[has_wiki_page]=no&limit=100&search[id]={",".join(map(str, (t.id for t in tag_batch)))}'

    body += """

        [tn]This is an automatic post. Use topic #31779 to report errors/false positives or general feedback.[/tn]
    """
    body = remove_indent(body)
    logger.info("Sending forum post:")
    logger.info(body)
    if POST_TO_PROD:
        danbooru_api.create_forum_post(
            topic_id=topic_id,
            body=body,
        )


def main() -> None:
    config = get_config("auto_submit_implications.yaml")

    default_pattern = re.compile(r"(?P<base_name>.*)_(?P<costume_name>\(.*?\))_(?P<series_name>\(.*?\))")

    series_list = [
        Series(**series | {
            "costume_patterns": [ast.literal_eval(p) for p in series.get("extra_costume_patterns", [])] + [default_pattern],
        })
        for series in config["series"]
    ]

    for series in series_list:
        process_series(series)


if __name__ == "__main__":
    main()
