from __future__ import annotations

import ast
import os
import re
import time
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from functools import cached_property
from itertools import batched
from typing import Literal

import click

from danboorutools import get_config, logger
from danboorutools.logical.sessions.danbooru import danbooru_api, kwargs_to_include
from danboorutools.models.danbooru import DanbooruBulkUpdateRequest  # noqa: TC001
from danboorutools.util.misc import BaseModel, remove_indent

logger.log_to_file()

BOT_DISCLAIMER = "[tn]This is an automatic post. Use topic #31779 to report errors/false positives or general feedback.[/tn]"

BOT_IMPLICATION_REASON = """
 [code]beep boop[/code]

I found costume tags that need an implications. Vote on this BUR and say something if you disagree.
"""

BOT_WIKILESS_HEADER = """
 [code]beep boop[/code]

I was going to submit an implication request for these tags, but they have no wiki page.
Write a wiki page for them and I'll be able to submit them next time I run.
"""


DEFAULT_COSTUME_PATTERN = re.compile(r"(?P<base_name>.*?)_(?P<qualifiers>\(.*\))_(?P<series_qualifier>\(.*?\))")

POSTED_THRESHOLD = datetime.now(UTC) - timedelta(weeks=2)
bot_username = os.environ["DANBOORU_BOT_USERNAME"]
bot_forum_posts = danbooru_api.forum_posts(
    body_matches="*Write a wiki page for them*",
    limit=1000,
    creator_name=bot_username,
    created_at=f">{danbooru_api.db_datetime(POSTED_THRESHOLD)}",
)


class DanbooruImplicationData(BaseModel):
    antecedent_name: str
    consequent_name: str


class DanbooruTagData(BaseModel):
    name: str
    id: int
    antecedent_implications: list[DanbooruImplicationData]
    wiki_page: dict | None = None

    def __hash__(self) -> int:
        return hash(f"{self.id}-{self.name}")


class Series(BaseModel):
    name: str
    topic_id: int

    extra_costume_patterns: list[re.Pattern]

    grep: str | None = None

    @cached_property
    def costume_patterns(self) -> list[re.Pattern[str]]:
        return [*self.extra_costume_patterns, DEFAULT_COSTUME_PATTERN]

    @property
    def topic_url(self) -> str:
        return f"https://danbooru.donmai.us/forum_topics/{self.topic_id}"

    @cached_property
    def burs(self) -> list[DanbooruBulkUpdateRequest]:
        total_burs = []
        page = 1
        while True:
            burs = danbooru_api.bulk_update_requests(script_ilike=f"*_({self.name})*", limit=1000, page=page)
            total_burs += burs

            if len(burs) < 1000:
                if not total_burs:
                    raise NotImplementedError
                return total_burs
            page += 1

    @cached_property
    def tags_with_burs(self) -> set[str]:
        return {tag for bur in self.burs for tag in bur.tags}

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
        filtered = filter(lambda tag: any(p.match(tag.name) for p in self.costume_patterns), self.all_tags)
        if self.grep:
            filtered = filter(lambda tag: self.grep in tag.name, filtered)  # type: ignore[arg-type] # stfu
        return list(filtered)

    @cached_property
    def tags_without_implications(self) -> list[DanbooruTagData]:
        tags_without_implications = [
            tag for tag in self.costume_tags
            if not tag.antecedent_implications
            and tag.name not in self.tags_with_burs
        ]
        logger.info(f"Found <r>{len(tags_without_implications)}</r> tags without an implication (pending or otherwise).")
        return tags_without_implications

    @cached_property
    def implicable_tags_without_wiki(self) -> list[DanbooruTagData]:
        return [t for ig in self.implication_groups for t in ig.tags_without_wiki]

    def get_possible_parents(self, name: str) -> list[str]:
        possible_parents = []

        for pattern in self.costume_patterns:
            if match := pattern.match(name):
                base_name = match.groupdict()["base_name"]
                series_qualifier = match.groupdict()["series_qualifier"]

                qualifiers = re.findall(r"(\(.*?\))", match.groupdict()["qualifiers"])

                for index in range(len(qualifiers)):
                    partial_qualifier = "_".join(qualifiers[:index])
                    possible_parents.append(f"{base_name}_{partial_qualifier}_{series_qualifier}")

                possible_parents.append(f"{base_name}_{series_qualifier}")

        return list({re.sub(r"_+", "_", p) for p in possible_parents})

    def search_for_main_tag(self, subtag_name: str) -> DanbooruTagData | None:
        potential_parents = sorted(self.get_possible_parents(subtag_name), key=lambda t: len(t), reverse=True)
        logger.trace(f"Found potential parents for {subtag_name}: {potential_parents}")
        for potential_parent in potential_parents:
            logger.trace(f"Checking if {potential_parent} for {subtag_name} exists.")
            for candidate in self.all_tags:
                if candidate.name == potential_parent:
                    logger.trace(f"> Parent tag name for {subtag_name} seems to be {candidate.name}.")
                    return candidate

            logger.trace("It did not.")

        logger.info(f"Could not determine parent for {subtag_name}, skipping.")
        return None

    @property
    def implication_groups(self) -> list[ImplicationGroup]:
        relationships = defaultdict(list)
        for tag in self.tags_without_implications:
            if parent_tag := self.search_for_main_tag(tag.name):
                relationships[parent_tag].append(tag)

        implication_groups = [
            ImplicationGroup(main_tag=main_tag, subtags=list(subtags), series=self)
            for main_tag, subtags in relationships.items()
        ]

        return sorted(implication_groups, key=lambda i: i.main_tag.name)

    def scan_and_post(self, bulk_mode_cli: Literal["yes", "no", "all"] = "no", post_to_danbooru: bool = False, post_wikiless_separately: bool = False) -> None:
        implications_per_bulk = 10

        if bulk_mode_cli == "yes":
            bulk_mode = len(self.implication_groups) > 5
        elif bulk_mode_cli == "no":
            bulk_mode = len(self.implication_groups) > 100_000
        elif bulk_mode_cli == "all":
            bulk_mode = len(self.implication_groups) > 1
            implications_per_bulk = 100
        else:
            raise NotImplementedError(bulk_mode_cli)

        logger.info(f"Processing series: {self.name}. Topic: {self.topic_url}.")
        logger.info(f"There are {len(self.implication_groups)} implication groups. Bulk mode: {bulk_mode}")

        counter = implications_per_bulk
        bur_script = ""
        tags_with_no_wikis = []

        posted = []

        bur_reason = BOT_IMPLICATION_REASON + "\n" + wikiless_tags_to_dtext(self.implicable_tags_without_wiki) + "\n" + BOT_DISCLAIMER

        for group in self.implication_groups:
            logger.info(f"Found implication group: {", ".join(tag.name for tag in group.subtags)} -> {group.main_tag.name} ")
            if group.tags_without_wiki:
                logger.info(f"There are {len(group.tags_without_wiki)} tags without a wiki here: {group.tags_without_wiki}.")
                tags_with_no_wikis += group.tags_without_wiki

            if not group.tags_with_wiki:
                logger.info("<r>This group has no tags with wiki. Moving on...</r>")
                continue

            if bulk_mode:
                counter -= len(group.tags_with_wiki)
                bur_script += group.script + "\n"

                if counter <= 0:
                    send_bur(self, bur_script, bur_reason, post_to_danbooru=post_to_danbooru)
                    posted += [bur_script]
                    bur_script = ""
                    counter = 10
            else:
                send_bur(self, group.script, bur_reason, post_to_danbooru=post_to_danbooru)
                posted += [group.script]

        if bur_script:
            send_bur(self, bur_script, bur_reason, post_to_danbooru=post_to_danbooru)
            posted += [bur_script]

        if post_wikiless_separately:
            post_tags_without_wikis(tags_with_no_wikis, self.topic_id, post_to_danbooru=post_to_danbooru)

        logger.info(f"In total, {len(posted)} BURs have been submitted.")
        for index, bur in enumerate(posted):
            logger.info(f"BUR #{index+1}:\n{bur}\n")

        logger.info(f"Topic of submission: {self.topic_url}")
        logger.info(f"Reason for BURs: {bur_reason}")


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


def send_bur(series: Series, script: str, reason: str, post_to_danbooru: bool) -> None:
    logger.info("Submitting implications:")
    logger.info(f"\n<c>{script}</c>")

    if post_to_danbooru:
        danbooru_api.create_bur(
            topic_id=series.topic_id,
            script=script,
            reason=reason,
        )


def post_tags_without_wikis(tags: list[DanbooruTagData], topic_id: int, post_to_danbooru: bool = False) -> None:
    body = BOT_WIKILESS_HEADER
    body += wikiless_tags_to_dtext(tags)
    body += f"\n\n{BOT_DISCLAIMER}"

    body = remove_indent(body)
    logger.info("Sending forum post:")
    logger.info(body)

    if post_to_danbooru:
        danbooru_api.create_forum_post(
            topic_id=topic_id,
            body=body,
        )
        time.sleep(1)


def wikiless_tags_to_dtext(tags: list[DanbooruTagData], only_unposted: bool = True) -> str:
    if only_unposted:
        tags = [t for t in tags if not any(f"[[{t.name}]]" in post.body for post in bot_forum_posts)]

    body = "\n[expand Tags without a wiki that couldn't be submitted]"
    for tag in tags:
        body += f"\n* [[{tag.name}]]"
    body += "\n[/expand]"

    will_be_batched = len(tags) > 100

    body += f"\n\nSelf-updating link{"s" if will_be_batched else ""} to all tags without wiki from the above list:"

    for index, tag_batch in enumerate(batched(tags, 100)):
        id_str = ",".join(map(str, (t.id for t in tag_batch)))
        link_number = f" #{index+1}" if will_be_batched else ""
        body += f'\n* "Link{link_number}":/tags?search[has_wiki_page]=no&limit=100&search[id]={id_str}'

    return body


def series_from_config(grep: str | None = None) -> list[Series]:
    config = get_config("auto_submit_implications.yaml")

    series_list = [
        Series(grep=grep, **series | {
            "extra_costume_patterns": [ast.literal_eval(p) for p in series.get("extra_costume_patterns", [])],
        })
        for series in config["series"]
    ]

    return series_list


@click.command()
@click.option("-s", "--series", nargs=1)
@click.option("-b", "--bulk_mode", type=click.Choice(["yes", "no", "all"]), default="no")
@click.option("-p", "--post_to_danbooru", is_flag=True, default=False)
@click.option("-pw", "--post_wikiless_separately", is_flag=True, default=False)
@click.option("-g", "--grep", nargs=1)
def main(series: str | None = None,
         bulk_mode: Literal["yes", "no", "all"] = "no",
         post_to_danbooru: bool = False,
         post_wikiless_separately: bool = False,
         grep: str | None = None) -> None:

    if series:
        logger.info(f"<r>Running only for series {series}.</r>")

    for config_series in series_from_config(grep=grep):
        if series and series.lower() != config_series.name.lower():
            continue
        config_series.scan_and_post(bulk_mode_cli=bulk_mode,
                                    post_to_danbooru=post_to_danbooru,
                                    post_wikiless_separately=post_wikiless_separately)
