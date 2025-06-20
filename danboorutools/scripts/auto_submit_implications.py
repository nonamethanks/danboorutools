from __future__ import annotations

import ast
import operator
import os
import re
import time
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from functools import cached_property, reduce
from itertools import batched
from typing import Literal

import click
from peewee import BooleanField, CharField, DateTimeField, IntegerField, Model, SqliteDatabase
from pydantic import Field

from danboorutools import get_config, logger, settings
from danboorutools.logical.sessions.danbooru import danbooru_api, kwargs_to_include
from danboorutools.models.danbooru import DanbooruBulkUpdateRequest, DanbooruTag
from danboorutools.util.bigquery import clone_bigquery_table
from danboorutools.util.misc import BaseModel, remove_indent

logger.log_to_file()

BOT_DISCLAIMER = "[tn]This is an automatic post. Use topic #31779 to report errors/false positives or general feedback.[/tn]"

BOT_IMPLICATION_REASON = """
 [code]beep boop[/code]
"""

BOT_WIKILESS_HEADER = """
 [code]beep boop[/code]

I was going to submit an implication request for these tags, but they have no wiki page.
Write a wiki page for them and I'll be able to submit them next time I run.
"""


DEFAULT_COSTUME_PATTERN = re.compile(r"(?P<base_name>[^(]+)(?P<qualifiers>(?:_\(.*\)))")

POSTED_THRESHOLD = datetime.now(UTC) - timedelta(weeks=2)
bot_username = os.environ["DANBOORU_BOT_USERNAME"]
bot_forum_posts = danbooru_api.forum_posts(
    body_matches="*Write a wiki page for them*",
    limit=1000,
    creator_name=bot_username,
    created_at=f">{danbooru_api.db_datetime(POSTED_THRESHOLD)}",
)


class TooManyBursError(Exception):
    ...


class DanbooruImplicationData(BaseModel):
    antecedent_name: str
    consequent_name: str


class DanbooruTagData(BaseModel):
    name: str
    id: int
    post_count: int
    antecedent_implications: list[DanbooruImplicationData]
    wiki_page: dict | None = None
    is_deprecated: bool

    def __hash__(self) -> int:
        return hash(f"{self.id}-{self.name}")

    def __repr__(self) -> str:
        return f"DanbooruTagData[id={self.id} name={self.name}]"

    @cached_property
    def qualifiers(self) -> list[str]:
        return re.findall(r"\((.*?)\)", self.name)

    def has_series_qualifier(self, qualifiers: list[str]) -> bool:
        return bool(self.qualifiers and self.qualifiers[-1] in qualifiers)

    def belongs_to_series(self, series: Series) -> bool:
        if self.has_series_qualifier(series.series_qualifiers):
            return True

        if not (known_copyrights := COPYRIGHT_MAP.get(self.name)):
            logger.debug(f"Searching for copyright for tag {self.name}...")
            tag_series = self.related_copyrights
            if not tag_series:
                logger.error(f"Copyrights for tag {self.name} could not be determined.")
                return False
            saved = TagCopyright(name=self.name, copyrights=",".join(tag_series))
            logger.debug(f"Saving copyright for {self.name} to DB...")
            saved.save()
            known_copyrights = saved.copyrights.split(",")  # type: ignore[attr-defined]
            COPYRIGHT_MAP[self.name] = known_copyrights
            assert known_copyrights

        return any(qualifier in known_copyrights for qualifier in series.series_qualifiers)

    def possible_parents(self, series: Series) -> list[str] | Literal[False]:
        all_possible_parents: list[str] = []

        matched_count = 0
        for pattern in series.costume_patterns:
            if not (match := pattern.match(self.name)):
                continue

            matched_count += 1
            possible_parents = []

            base_name = match.groupdict()["base_name"]
            extra_qualifier = match.groupdict().get("extra_qualifier")
            try:
                qualifiers = re.findall(r"(\(.*?\))", match.groupdict()["qualifiers"])
            except Exception as e:
                raise NotImplementedError(self, pattern, match.groupdict()) from e

            qualifiers = [q.strip("_") for q in [extra_qualifier, *qualifiers] if q]

            series_qualifier_pattern = rf"_\({series.qualifiers_pattern}\)$"
            if re.search(series_qualifier_pattern, self.name):
                [*qualifiers, series_qualifier] = qualifiers
            else:
                series_qualifier = None

            for index in range(len(qualifiers)):
                partial_qualifier = "_".join(qualifiers[:index])

                possible_parent = f"{base_name}_{partial_qualifier}"
                if series_qualifier:
                    possible_parent = f"{possible_parent}_{series_qualifier}"

                possible_parent = re.sub(r"_+", "_", possible_parent).strip("_")
                if possible_parent == self.name:
                    continue

                possible_parents.append(possible_parent)

            if len(possible_parents) == 0:
                matched_count -= 1
            all_possible_parents += possible_parents

        if not matched_count:
            return False

        return list(dict.fromkeys(all_possible_parents))

    @cached_property
    def related_copyrights(self) -> list[str]:
        related_tags = danbooru_api.danbooru_request(
            "GET",
            "related_tag.json",
            params=kwargs_to_include(
                category="Copyright",
                query=self.name,
                limit=10,
            ),
        )["related_tags"]
        related_tags = [r["tag"]["name"] for r in related_tags if r["frequency"] > 0.9]
        return related_tags


class Series(BaseModel):
    name: str
    topic_id: int

    wiki_ids: list[int] = Field(default_factory=list)

    extra_costume_patterns: list[re.Pattern]
    extra_qualifiers: list[str] = Field(default_factory=list)

    line_blacklist: list[str] = Field(default_factory=list)
    qualifier_blacklist: list[str] = Field(default_factory=list)

    grep: str | None = None

    autopost: bool = False

    MAX_BURS_PER_TOPIC: int = 10
    POSTED_BURS: int = 0

    group_by_qualifier: bool = True
    allow_sub_implications: bool = True

    def __hash__(self) -> int:
        return hash(f"{self.topic_id}-{self.name}")

    @cached_property
    def costume_patterns(self) -> list[re.Pattern[str]]:
        return [*self.extra_costume_patterns, DEFAULT_COSTUME_PATTERN]

    @property
    def series_qualifiers(self) -> list[str]:
        return [self.name, *self.extra_qualifiers]

    @cached_property
    def qualifiers_pattern(self) -> str:
        all_qualifiers = "|".join([re.escape(n) for n in self.series_qualifiers])

        qualifier_group = rf"(?:{all_qualifiers})"
        return qualifier_group

    @property
    def topic_url(self) -> str:
        return f"https://danbooru.donmai.us/forum_topics/{self.topic_id}"

    @cached_property
    def series_burs(self) -> list[DanbooruBulkUpdateRequest]:
        results = danbooru_api.get_all(
            DanbooruBulkUpdateRequest,
            script_ilike=f"*_({self.name})*",
        )
        return results

    @cached_property
    def topic_burs(self) -> list[DanbooruBulkUpdateRequest]:
        return danbooru_api.get_all(
            DanbooruBulkUpdateRequest,
            forum_topic_id=self.topic_id,
        )

    @property
    def remaining_bur_slots(self) -> int:
        return self.MAX_BURS_PER_TOPIC - len([t for t in self.topic_burs if t.status == "pending"]) - self.POSTED_BURS

    @cached_property
    def existing_implication_requests(self) -> dict[str, list[str]]:
        burs = self.series_burs
        known_bur_ids = [b.id for b in burs]
        burs += [b for b in self.topic_burs if b.id not in known_bur_ids]

        parsed: dict[str, list[str]] = defaultdict(list)
        for bur in burs:
            for bur_line in bur.script.lower().split("\n"):

                if not bur_line.startswith(("create implication", "imply")):
                    continue

                line = re.sub(r"\s+", " ", bur_line).strip()
                if not line:
                    continue

                line = line.removeprefix("create implication").removeprefix("imply").strip()
                try:
                    antecedent, consequent = line.split(" -> ")
                except ValueError as e:
                    e.add_note(f"On '{line}'")
                    raise
                if " " in antecedent or " " in consequent:
                    raise NotImplementedError(antecedent, consequent, bur_line)
                parsed[antecedent] += [consequent]

        return parsed

    @cached_property
    def all_tags_from_search(self) -> list[DanbooruTagData]:
        tags = []
        for qualifier in self.series_qualifiers:
            tags += danbooru_api.get_all(
                DanbooruTag,
                to_model=DanbooruTagData,
                name_matches=f"*_({qualifier})",
                category=4,
                order="id",
                hide_empty=True,
                is_deprecated=False,
                only="id,name,post_count,antecedent_implications,wiki_page,is_deprecated",
            )

        return tags

    @cached_property
    def all_tags_from_wiki(self) -> list[DanbooruTagData]:
        if not self.wiki_ids:
            return []

        all_tags_from_search = self.all_tags_from_search

        wiki_pages = danbooru_api.wiki_pages(id=",".join(map(str, self.wiki_ids)))
        logger.info(f"Fetching tags for {self.name} from wiki pages {[wiki.url for wiki in wiki_pages]}...")

        tag_names = []
        for wiki in wiki_pages:
            logger.info(f"Processing wiki page '{wiki.title}'")
            tag_names += wiki.get_linked_tags()
            assert tag_names
            tag_names = [t for t in tag_names if t not in [t.name for t in all_tags_from_search]]
            if not tag_names:
                continue
            logger.info(f"Found {len(tag_names)} in wikis so far.")

        if not tag_names:
            return []

        tags = BigqueryTag.get_db_tags(tag_names)

        processed_tags = []
        logger.info("Filtering out extraneous tags...")

        for tag in tags:
            if tag.post_count < 5:  # skip small tags
                continue
            if not tag.belongs_to_series(self):
                logger.debug(f"Tag {tag.name} does not belong to {self.name}. Skipping...")
                continue
            processed_tags += [tag]
        logger.info(f"Remaining: {len(processed_tags)}.")

        processed_tags += self.get_child_tags_from_db(processed_tags)

        logger.info(f"Done processing tags from wikis, {len(processed_tags)} found.")
        return processed_tags

    def get_child_tags_from_db(self, parent_tags: list[DanbooruTagData]) -> list[DanbooruTagData]:
        child_ids: list[int] = []
        clauses = [BigqueryTag.name.startswith(tag.name) for tag in parent_tags]
        for batch in batched(clauses, 50):
            children = BigqueryTag.select() \
                .where(BigqueryTag.category == 4) \
                .where(reduce(operator.or_, batch)) \
                .where(~(BigqueryTag.name << [t.name for t in parent_tags]))
            child_ids += [child["id"] for child in children.dicts()]

        if not child_ids:
            return []

        child_tags = BigqueryTag.get_db_tags(
            tag_ids=child_ids,
            has_antecedent_implications=False,
        )

        vetted_child_tags = []

        for child_tag in child_tags:
            if not child_tag.belongs_to_series(self):
                logger.debug(f"Potential child tag {child_tag.name} does not belong to {self.name}. Skipping...")
                continue
            vetted_child_tags += [child_tag]

        return vetted_child_tags

    @cached_property
    def all_tag_map(self) -> dict[str, DanbooruTagData]:
        return {t.name: t for t in self.all_tags_from_wiki + self.all_tags_from_search}

    def get_parent_for_tag(self, tag: DanbooruTagData) -> DanbooruTagData | None:
        if tag.antecedent_implications:
            return None

        if set(tag.qualifiers) & set(self.qualifier_blacklist):
            return None

        possible_parents = tag.possible_parents(self)

        if possible_parents is False:
            return None

        if not possible_parents:
            logger.trace(f"Could not determine a parent for {tag.name}")
            return None

        possible_parents.sort(key=lambda t: len(t), reverse=self.allow_sub_implications)
        for parent_name in possible_parents:
            if f"{tag.name} -> {parent_name}" in self.line_blacklist:
                logger.trace(f"Skipping {tag.name} -> {parent_name} because this implication was blacklisted.")
                continue

            if not (parent := self.all_tag_map.get(parent_name)):
                continue

            if parent.is_deprecated:
                continue

            return parent

        logger.trace(f"Could not find an existing parent for {tag.name}")
        return None

    def should_skip_implication(self, _from: DanbooruTagData, to: DanbooruTagData) -> bool:
        if to.name in self.existing_implication_requests.get(_from.name, []):
            logger.trace(f"Skipping {_from.name} -> {to.name} because this implication was already requested.")
            return True

        return False

    @cached_property
    def implication_groups(self) -> list[ImplicationGroup]:
        logger.debug(
            f"{len(self.all_tags_from_wiki)} (from wiki) + {len(self.all_tags_from_search)} (from search) = "
            f"{len(self.all_tags_from_wiki) + len(self.all_tags_from_search)} tags to process.",
        )

        parent_children_map: defaultdict[DanbooruTagData, list[DanbooruTagData]] = defaultdict(list)
        for tag in self.all_tag_map.values():
            if not (parent := self.get_parent_for_tag(tag)):
                continue

            if self.should_skip_implication(_from=tag, to=parent):
                continue

            parent_children_map[parent] += [tag]

        implication_groups = [ImplicationGroup(main_tag=main_tag, subtags=subtags, series=self)
                              for main_tag, subtags in parent_children_map.items()]
        implication_groups.sort(key=lambda x: x.main_tag.name)

        return implication_groups

    @cached_property
    def implication_groups_by_qualifier(self) -> list[list[ImplicationGroup]]:
        # attempt to group implication groups by qualifier if they're single-tag groups
        grouped_by_qualified: list[list[ImplicationGroup]] = []
        grouped_by_character: list[list[ImplicationGroup]] = []

        qualifier_map: defaultdict[ImplicationGroup, list[str]] = defaultdict(list)
        qualifier_count: defaultdict[str, int] = defaultdict(int)

        for group in self.implication_groups:
            if len(group.subtags) > 1:
                grouped_by_character += [[group]]
                continue

            inserted = False
            for qualifier in group.subtags[0].qualifiers:
                if qualifier in self.series_qualifiers:
                    continue
                qualifier_map[group].append(qualifier)
                qualifier_count[qualifier] += 1
                inserted = True

            if not inserted:
                grouped_by_character += [[group]]

        for qualifier, _ in sorted(qualifier_count.items(), key=lambda item: item[1], reverse=True):
            by_qualifier = [group for group in qualifier_map if qualifier in qualifier_map[group]]
            if len(by_qualifier) > 1:
                grouped_by_qualified += [by_qualifier]
            elif by_qualifier:
                grouped_by_character += [by_qualifier]

            for group in by_qualifier:
                del qualifier_map[group]

        if len(qualifier_map) > 0:
            for ig, leftover_qualifiers in qualifier_map.items():
                subtags = [subtag.name for subtag in ig.subtags]
                logger.warning(f"Leftover qualifier {leftover_qualifiers} -> {subtags}. This should not happen.")
            raise NotImplementedError("Shouldn't be anything else left.")

        total = grouped_by_qualified + sorted(grouped_by_character, key=lambda g: g[0].main_tag.name)
        return total

    @cached_property
    def implicable_tags_without_wiki(self) -> list[DanbooruTagData]:
        tags = [t for ig in self.implication_groups for t in ig.tags_without_wiki]
        tags.sort(key=lambda tag: tag.name)
        return tags

    def scan_and_post(self, max_lines_per_bur: int = 1) -> None:
        logger.info(f"Processing series: {self.name}. Topic: {self.topic_url}.")
        logger.info(f"There are {len(self.implication_groups)} implication groups. "
                    f"Max lines per BUR: {max_lines_per_bur}.")
        logger.info(f"Remaining amount of BURs that can be posted {self.topic_url}: {self.remaining_bur_slots}.")

        counter = max_lines_per_bur
        bur_script = ""
        tags_with_no_wikis = []

        posted = []

        bur_reason = BOT_IMPLICATION_REASON + "\n" + wikiless_tags_to_dtext(self.implicable_tags_without_wiki) + "\n" + BOT_DISCLAIMER

        groups_by_qualifier = self.implication_groups_by_qualifier if self.group_by_qualifier \
            else [[group] for group in self.implication_groups]

        for qualifier_groups in groups_by_qualifier:
            for group in qualifier_groups:
                logger.debug(f"Found implication group: {", ".join(tag.name for tag in group.subtags)} -> {group.main_tag.name} ")
                if group.tags_without_wiki:
                    logger.debug(f"There are {len(group.tags_without_wiki)} tags without a wiki here: {group.tags_without_wiki}.")
                    tags_with_no_wikis += group.tags_without_wiki

                if not group.tags_with_wiki:
                    logger.debug("<r>This group has no tags with wiki. Moving on...</r>")
                    continue

                counter -= len(group.tags_with_wiki)
                bur_script += group.script + "\n"

            if counter <= 0:
                self.send_bur(bur_script, bur_reason)
                posted += [bur_script]
                bur_script = ""
                counter = max_lines_per_bur

        if bur_script:
            self.send_bur(bur_script, bur_reason)
            posted += [bur_script]

        logger.info(f"In total, {len(posted)} BURs {"would " if not self.autopost else ""}have been submitted.")
        if len(posted):
            burs = [f"[expand BUR #{index+1}]\n{"\n".join(sorted(bur.splitlines()))}\n[/expand]"
                    for index, bur in enumerate(posted)]
            logger.info("\n\n" + "\n\n".join(burs))

        logger.info(f"Topic of submission: {self.topic_url}")
        logger.info(f"Reason for BURs: {bur_reason}")

    def matches(self, name: str) -> bool:
        bad_chars = "!?."
        matches = [
            name.strip(bad_chars).replace("_", " ")
            for name in [self.name, *self.extra_qualifiers]
        ]
        return name.strip(bad_chars).replace("_", " ") in matches

    def send_bur(self, script: str, reason: str) -> None:

        logger.info("Submitting implications:")

        script = "\n".join(sorted(script.splitlines()))

        logger.info(f"\n<c>{script}</c>")

        if self.autopost:
            if self.remaining_bur_slots <= 0:
                raise TooManyBursError
            danbooru_api.create_bur(
                topic_id=self.topic_id,
                script=script,
                reason=reason,
            )
            self.POSTED_BURS += 1


class ImplicationGroup(BaseModel):
    main_tag: DanbooruTagData
    subtags: list[DanbooruTagData]

    series: Series

    def __hash__(self) -> int:
        return hash(f"{self.main_tag}-{self.subtags}")

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


def wikiless_tags_to_dtext(tags: list[DanbooruTagData]) -> str:
    if not tags:
        return ""

    body = "\n[expand Tags without a wiki that couldn't be submitted]"
    for tag in tags:
        body += f"\n* [[{tag.name}]]"
    body += "\n[/expand]\n"

    will_be_batched = len(tags) > 100

    for index, tag_batch in enumerate(batched(tags, 100)):
        link = f"/tags?search[has_wiki_page]=no&limit=100&search[id]={",".join(map(str, (t.id for t in tag_batch)))}"
        link_number = f" #{index+1}" if will_be_batched else ""
        link_description = f"Link{link_number} to tags that couldn't be submitted"
        body += f'\n* "{link_description}":{link}'

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


tag_database = SqliteDatabase(settings.BASE_FOLDER / "data" / "bigquery_tags.sqlite")


class TagCopyright(Model):
    class Meta:
        database = tag_database

        indexes = (
            (("name",), True),
        )

    name = CharField(index=True, unique=True)
    copyrights = CharField(index=True)


COPYRIGHT_MAP = {tag["name"]: tag["copyrights"].split(",") for tag in TagCopyright.select().dicts()}


class BigqueryTag(Model):
    class Meta:
        database = tag_database

    id = IntegerField(primary_key=True)
    name = CharField(index=True)
    post_count = IntegerField(index=True)
    category = IntegerField(index=True)
    created_at = DateTimeField(index=True)
    updated_at = DateTimeField(index=True)
    is_deprecated = BooleanField(index=True)

    @staticmethod
    def get_db_tags(tag_names: list[str] | None = None, tag_ids: list[int] | None = None, **kwargs) -> list[DanbooruTagData]:
        if not tag_ids:
            if not tag_names:
                raise ValueError("Tag names are required.")

            chartags = BigqueryTag.select(BigqueryTag.id)\
                .where(BigqueryTag.name << tag_names)\
                .where(BigqueryTag.category == 4)\
                .dicts()

            tag_ids = [chartag["id"] for chartag in chartags]
            if not tag_ids:
                return []

        tags: list[DanbooruTagData] = []
        for tag_id_group in batched(tag_ids, 100):
            tags += danbooru_api.get_all(
                DanbooruTag,
                to_model=DanbooruTagData,
                id=",".join(map(str, tag_id_group)),
                category=4,
                order="id",
                hide_empty=True,
                is_deprecated=False,
                only="id,name,post_count,antecedent_implications,wiki_page,is_deprecated",
                **kwargs,
            )
        return tags


BigqueryTag.add_index(BigqueryTag.name, BigqueryTag.category)


@click.command()
@click.option("-s", "--series", nargs=1)
@click.option("-m", "--max-lines-per-bur", nargs=1, default=1, type=click.IntRange(1, 100))
@click.option("-p", "--post_to_danbooru", is_flag=True, default=False)
@click.option("-g", "--grep", nargs=1)
def main(series: str | None = None,
         max_lines_per_bur: int = 1,
         post_to_danbooru: bool = False,
         grep: str | None = None) -> None:

    logger.info("Updating the tags db...")
    with tag_database:
        tag_database.create_tables([TagCopyright])
    clone_bigquery_table("tags", model=BigqueryTag, database=tag_database)

    if series:
        logger.info(f"<r>Running only for series {series}.</r>")

    for config_series in series_from_config(grep=grep):
        if series and not config_series.matches(series):
            continue

        config_series.autopost = post_to_danbooru
        try:
            config_series.scan_and_post(max_lines_per_bur=max_lines_per_bur)
        except TooManyBursError:
            logger.error(f"Too many BURs for '{config_series.name}' in {config_series.topic_url}. Stopping now. Go approve some!")
