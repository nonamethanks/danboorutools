from __future__ import annotations

import readline
import sys
import termios
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

import click
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from danboorutools import logger, settings
from danboorutools.logical.sessions.danbooru import danbooru_api, kwargs_to_include
from danboorutools.models.danbooru import DanbooruUser
from danboorutools.util.misc import remove_indent

f_path = logger.log_to_file()

END_DATE = datetime.now(tz=UTC) + timedelta(days=1)
START_DATE = datetime.now(tz=UTC) - timedelta(days=60)

MIN_CONTRIBUTOR_UPLOADS_IN_RANGE = 20
MIN_UPLOADS_WITH_EDITS = 500
MIN_STANDALONE_UPLOADS = 500
MIN_EDITS_WITH_UPLOADS = 3000
MIN_STANDALONE_EDITS = 5000
CONTRIB_RISKY_DEL_COUNT = 20
CONTRIB_MAX_DEL_COUNT = 50
CONTRIB_MAX_DEL_PERC = 3
BUILDER_MAX_DEL_PERC = 15
MIN_NOTES = 2000


def input_with_prefill(prompt: str, text: str) -> str:
    #  # https://stackoverflow.com/questions/8505163/is-it-possible-to-prefill-a-input-in-python-3s-command-line-interface
    def hook() -> None:
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result


class Ignored:
    file_path = Path(settings.BASE_FOLDER / "data" / "promotion_ignored.txt")

    @classmethod
    def add(cls, user_id: int, show_again_in_days: int) -> None:
        data = cls.get_all()
        data[user_id] = datetime.now(tz=UTC) + timedelta(days=show_again_in_days)

        logger.info(f"Hiding user {user_id} for {show_again_in_days} days.")

        data = {k: v for (k, v) in data.items() if v > datetime.now(tz=UTC)}
        with cls.file_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(f"{user_id},{datetime.timestamp()}" for (user_id, datetime) in data.items()))

    @classmethod
    def get_all(cls) -> dict[int, datetime]:
        if not cls.file_path.exists():
            return {}
        with cls.file_path.open("r+", encoding="utf-8") as f:
            data = {int(user_id): datetime.fromtimestamp(float(show_again_on_date), tz=UTC)
                    for (user_id, show_again_on_date) in (line.strip().split(",") for line in f.readlines())}

        data = {k: v for (k, v) in data.items() if v > datetime.now(tz=UTC)}
        return data


ignored = Ignored.get_all()
logger.info(f"There are {len(ignored)} ignored users.")


class Notes:

    file_path = Path(settings.BASE_FOLDER / "data" / "promotion_notes.txt")

    @classmethod
    def add(cls, user_id: int) -> None:
        note = input_with_prefill("Enter note: \n", notes.get(user_id, "")).strip()
        if not note:
            logger.info("No note added.")
            return
        notes[user_id] = note

        logger.info(f"Added note to user #{user_id}.")

        with cls.file_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(f"{user_id},{note}" for (user_id, note) in notes.items()))

    @classmethod
    def get_all(cls) -> dict[int, str]:
        if not cls.file_path.exists():
            return {}
        with cls.file_path.open("r+", encoding="utf-8") as f:
            data = {int(user_id): note for (user_id, note) in (line.strip().split(",") for line in f.readlines())}
        return data


notes = Notes.get_all()


@click.command("cli", context_settings={"show_default": True})
@click.option("--skip-to", "-s", "skip_to", default=0)
@click.option("--manual", "-m", is_flag=True, default=False)
@click.option("--reverse", "-r", is_flag=True, default=False)
@click.option("--ignore-ignored", "-i", is_flag=True, default=False)
@click.option("--min-uploads", "-u", "min_uploads", default=0)
@click.option("--level", "-l", "level", required=False, type=click.Choice(["member", "platinum", "gold", "builder", "nonbuilder", "all"], case_sensitive=False), default="all")
@click.argument("user_url", required=False, nargs=1)
def main(user_url: str | None,
         skip_to: int,
         manual: bool = False,
         reverse: bool = False,
         ignore_ignored: bool = False,
         min_uploads: int = 0,
         level: Literal["member", "platinum", "gold", "builder", "nonbuilder", "all"] = "all",
         ) -> None:
    if not user_url:
        suggest_promotions(skip_to=skip_to, manual=manual, reverse=reverse,
                           min_uploads=min_uploads, ignore_ignored=ignore_ignored, level=level)
    else:
        user = DanbooruUser.get_from_id(DanbooruUser.id_from_url(user_url))
        candidate = HTMLUser(name=user.name, recent_uploads=None, recent_deleted=None)
        merge_candidate(candidate, user)
        candidate.refresh()
        manual_loop([candidate])


def suggest_promotions(skip_to: int = 0, manual: bool = False, reverse: bool = False, min_uploads: int = 0, ignore_ignored: bool = False, level: str = "all") -> None:
    logger.info("Gathering data...")

    recent_uploaders = get_recent_uploaders()

    biggest_uploaders = get_biggest_non_contributor_uploaders()
    biggest_gardeners = get_biggest_non_builder_gardeners()
    biggest_translators = get_biggest_non_builder_translators()
    biggest_non_uploaders = biggest_gardeners | biggest_translators

    candidates: list[Candidate] = []

    for uploader in recent_uploaders:
        if (match := biggest_uploaders.get(uploader.name)):
            merge_candidate(uploader, match)
            candidates.append(uploader)

        elif (match := biggest_non_uploaders.pop(uploader.name, None)):
            merge_candidate(uploader, match)
            candidates.append(uploader)

        else:
            # user does not have enough uploads or edits to be considered
            pass

    manual_cycle = []

    if not manual:
        logger.info("Contributor candidates:")
    for candidate in candidates:
        if candidate.for_contributor:
            if manual:
                manual_cycle.append(candidate)
            else:
                logger.info(candidate.self_string)

    if not manual:
        logger.info("")
        logger.info("Builder/Contributor candidates:")

    for candidate in candidates:
        if candidate.for_builder:
            if manual:
                manual_cycle.append(candidate)
            else:
                logger.info(candidate.self_string)

    logger.info("")
    remaining: list[Candidate] = []
    if biggest_non_uploaders.values():
        for match in biggest_non_uploaders.values():
            # remaining gardeners that weren't caught with the previous pop
            if match.post_update_count > MIN_STANDALONE_EDITS or match.note_update_count > MIN_NOTES:
                candidate = HTMLUser(
                    name=match.name,
                    recent_uploads=None,
                    recent_deleted=None,
                )
                merge_candidate(candidate, match)
                remaining.append(candidate)

    generate_html(*candidates, *remaining)

    if remaining and not manual:
        logger.info("Builder candidates:")
        for candidate in [c for c in remaining if c.level != 32 and c.active]:
            logger.info(candidate.self_string)

    if manual:
        candidates = manual_cycle + [c for c in remaining if c.level != 32 and c.active]
        seen = {}
        for c in candidates:
            if c.id not in seen:
                seen[c.id] = c
        candidates = list(seen.values())
        candidates.sort(key=lambda c: c.sorted_weight, reverse=not reverse)
        if min_uploads:
            candidates = [c for c in candidates if c.total_uploads > min_uploads]
        if not ignore_ignored:
            candidates = [c for c in candidates if c.id not in ignored]
        if level:
            candidates = [
                c for c in candidates
                if (
                    level == "all"
                    or c.level_string == level.capitalize()
                    or (level == "nonbuilder" and c.level != 32)
                )
            ]
        manual_loop(candidates, index=skip_to)


def generate_html(*candidates: HTMLUser) -> None:
    env = Environment(  # noqa: S701
        loader=FileSystemLoader(settings.BASE_FOLDER / "danboorutools" / "templates"),
        undefined=StrictUndefined,
    )
    template = env.get_template("promotions.jinja2")

    generation_date = datetime.now(tz=UTC)

    sorted_candidates = sorted({user.name: user for user in candidates}.values(), key=lambda c: c.sorted_weight, reverse=True)
    output_from_parsed_template = template.render(
        generated_on=f"{generation_date:%Y-%m-%d at %T}",
        generated_on_unix=int(generation_date.timestamp() * 1000),
        builder_to_contributor=[c for c in sorted_candidates if c.for_contributor and c.level >= 32],
        member_to_contributor=[c for c in sorted_candidates if c.for_contributor and c.level < 32],
        rest=[c for c in sorted_candidates if not c.for_contributor],
        contrib_max_del_perc=CONTRIB_MAX_DEL_PERC,
        builder_max_del_perc=BUILDER_MAX_DEL_PERC,
        week=f"{generation_date:%U}",
        year=generation_date.year,
        max_deleted_bad=CONTRIB_MAX_DEL_COUNT,
        max_deleted_warning=CONTRIB_RISKY_DEL_COUNT,
    )
    Path("promotions.html").write_text(output_from_parsed_template, encoding="utf-8")


def manual_loop(candidates: list[HTMLUser], index: int = 0) -> None:
    index = index - 1 if index else 0
    while True:
        if not candidates:
            logger.info("No candidates left. Quitting.")
            break
        candidate = candidates[index]
        assert candidate.id
        try:
            logger.info(candidate.self_presentation(raise_on_old=len(candidates) > 1))
        except NoRecentEditsError:
            logger.error(f"No recent edits for user {candidate.id}. Skipping to the next...")
            Ignored.add(candidate.id, show_again_in_days=90)
            del candidates[index]
            continue
        logger.info(f"Candidate {index + 1} of {len(candidates)}. {len(candidates) - index - 1} candidates left.")

        while True:
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)

            if candidate.recent_deleted > 50:
                days_to_hide = 60
            elif candidate.level == 32:
                days_to_hide = 30
            else:
                days_to_hide = 10
            logger.info(f"Candidate will be hidden for <r>{days_to_hide}</r> days.")

            logger.info("<r>[Enter]</>Next <r>(default)</r> / "
                        "<r>[P]</>rev / "
                        "<r>[C]</>alculate edits / "
                        "<r>[R]</>efresh / "
                        "<r>[N]</>ote / "
                        "Hide for <r>[1-9]</>0 Days")
            if (_input := input("").strip().lower()) in [""]:
                Ignored.add(candidate.id, show_again_in_days=days_to_hide)
                index += 1
                if index >= len(candidates):
                    logger.info("No more candidates.")
                    return
                else:
                    break
            elif _input in ["p"]:
                index -= 1
                if index < 0:
                    logger.error("No previous candidates.")
                    index = 0
                else:
                    break
            elif _input in ["r"]:
                candidate.refresh(hard_refresh=True)
                break
            elif _input in ["n"]:
                Notes.add(candidate.id)
                break
            elif _input in ["c"]:
                candidate.calculate_post_edits()
                break
            elif _input in list(map(str, range(1, 10))):
                Ignored.add(candidate.id, show_again_in_days=int(f"{_input}0"))
                index += 1
                break
            else:
                logger.error("Invalid output.")


def merge_candidate(candidate: HTMLUser | Candidate, user: DanbooruUser) -> None:
    candidate.id = user.id
    candidate.total_uploads = user.post_upload_count
    candidate.total_edits = user.post_update_count
    candidate.total_notes = user.note_update_count
    candidate.level = user.level
    candidate.level_string = user.level_string
    candidate.is_deleted = user.is_deleted
    candidate.is_banned = user.is_banned


def get_recent_uploaders() -> list[HTMLUser]:
    query = {
        "from": START_DATE.strftime("%Y-%m-%d"),
        "to": END_DATE.strftime("%Y-%m-%d"),
        "group": "uploader",
        "group_limit": 1000,
        "uploader": {
            "level": "<35",
        },
    }

    recent_uploaders_data: list[dict] = danbooru_api.danbooru_request("GET", "/reports/posts.json", params=kwargs_to_include(**query))
    recent_deleted_data: list[dict] = danbooru_api.danbooru_request(
        "GET",
        "/reports/posts.json",
        params=kwargs_to_include(**query, tags="status:deleted"),
    )

    deleted_map = {d["uploader"]: d["posts"] for d in recent_deleted_data}

    recent_uploaders: list[HTMLUser] = []

    for uploader_data in recent_uploaders_data:
        name = uploader_data["uploader"]
        recent_uploaders.append(HTMLUser(
            name=name.replace(" ", "_"),
            recent_uploads=uploader_data["posts"],
            recent_deleted=deleted_map.get(name, 0)),
        )

    return recent_uploaders


def get_biggest_non_contributor_uploaders() -> dict[str, DanbooruUser]:
    page = 1
    uploaders: dict[str, DanbooruUser] = {}
    while True:
        last_fetched = danbooru_api.users(
            order="post_upload_count",
            post_upload_count=f">{MIN_UPLOADS_WITH_EDITS}",
            page=page,
            level="<35",
        )
        if not last_fetched:
            return uploaders
        uploaders |= {user.name: user for user in last_fetched}
        page += 1


def get_biggest_non_builder_gardeners() -> dict[str, DanbooruUser]:
    page = 1
    gardeners: dict[str, DanbooruUser] = {}
    while True:
        last_fetched = danbooru_api.users(
            order="post_update_count",
            post_update_count=f">{MIN_EDITS_WITH_UPLOADS}",
            page=page,
            level="<32",
            is_banned=False,
        )
        if not last_fetched:
            return gardeners
        gardeners |= {user.name: user for user in last_fetched}
        page += 1


def get_biggest_non_builder_translators() -> dict[str, DanbooruUser]:
    page = 1
    translators: dict[str, DanbooruUser] = {}
    while True:
        last_fetched = danbooru_api.users(
            order="note_update_count",
            note_update_count=f">{MIN_NOTES}",
            page=page,
            level="<32",
            is_banned=False,
        )
        if not last_fetched:
            return translators
        translators |= {user.name: user for user in last_fetched}
        page += 1


@dataclass
class Candidate:
    name: str
    recent_uploads: int | None
    recent_deleted: int | None

    is_deleted: bool | None = None
    is_banned: bool | None = None

    total_uploads: int | None = None
    total_edits: int | None = None
    total_notes: int | None = None
    id: int | None = None
    level: int | None = None
    level_string: str | None = None

    last_edit_date: datetime | None = None

    post_edit_details = ""

    @property
    def safe_name(self) -> str:
        return quote_plus(self.name)

    @property
    def active(self) -> bool:
        if self.is_deleted:   # can also be None
            return False
        if self.is_banned:  # can also be None  # noqa: SIM103
            return False
        return True

    @property
    def sorted_weight(self) -> int:
        return self.total_uploads + (self.total_edits / 10)

    @property
    def for_contributor(self) -> bool:
        if self.recent_uploads is None:
            self.refresh()
            assert self.recent_uploads is not None
        return self.active and self.recent_uploads > MIN_CONTRIBUTOR_UPLOADS_IN_RANGE and self.total_uploads > MIN_STANDALONE_UPLOADS

    @property
    def for_builder(self) -> bool:
        return self.active and self.level != 32

    @property
    def url(self) -> str:
        return f"https://danbooru.donmai.us/users/{self.id}"

    @property
    def uploads_url(self) -> str:
        return f"https://danbooru.donmai.us/posts?tags=user:{self.safe_name}+age:%3C2mo"

    @property
    def deleted_url(self) -> str:
        return f"{self.uploads_url}+status:deleted"

    @property
    def edits_url(self) -> str:
        return f"https://danbooru.donmai.us/post_versions?search[updater_name]={self.safe_name}&search[is_new]=false"

    @property
    def notes_url(self) -> str:
        return f"https://danbooru.donmai.us/note_versions?search[updater_name]={self.safe_name}"

    @property
    def self_string(self) -> str:
        length = 25 - (len(self.name) - len(self.name.encode("ascii", "ignore")))
        string = f"<{self.level_color}>{self.name:>{length}} </{self.level_color}> | "

        contributions = self.total_uploads + (self.total_edits / 10)
        combined_threshold = MIN_UPLOADS_WITH_EDITS + (MIN_EDITS_WITH_UPLOADS / 10)

        if self.level < 32:
            if (contributions > combined_threshold) or (self.total_uploads > 1000 or self.total_edits > 5000):
                edit_color = "<GREEN>"
            elif (self.total_edits > MIN_EDITS_WITH_UPLOADS or self.total_uploads > MIN_UPLOADS_WITH_EDITS):
                edit_color = "<YELLOW>"
            else:
                edit_color = "<WHITE>"
            string += f"{edit_color} {self.total_edits:>6} E, {self.total_uploads:>6} U {"</>" if edit_color else ""} | "
        else:
            string += f"{self.total_uploads:>6} U | "

        string += f"{self.recent_uploads if self.recent_uploads is not None else "???":>6} / {self.recent_deleted_colored} = {self.delete_ratio_colored} | "  # noqa: E501

        string += f" {self.url}"

        return string

    def refresh(self, hard_refresh: bool = False) -> None:
        logger.info(f"Refreshing data for user {self.name}...")
        date_tag = f"date:{danbooru_api.db_datetime(START_DATE, precision="day")}..{danbooru_api.db_datetime(END_DATE, precision="day")}"
        tags = [f"user:{self.name}", date_tag]
        self.last_edit_date = danbooru_api.get_last_edit_time(user_name=self.name)
        if self.last_edit_date < START_DATE:
            self.recent_uploads = 0
            self.recent_deleted = 0
        else:
            self.recent_uploads = danbooru_api.post_counts(tags=tags, hard_refresh=hard_refresh)
            self.recent_deleted = danbooru_api.post_counts(tags=[*tags, "status:deleted"], hard_refresh=hard_refresh)

        if hard_refresh or None in [self.total_notes, self.total_edits, self.total_uploads]:
            user, = danbooru_api.users(id=self.id)
            merge_candidate(self, user)
        logger.info("Refreshed.")

    def calculate_post_edits(self) -> None:
        if self.post_edit_details:
            return

        logger.info("Collecting post edits.")
        page = 1

        data = {}
        total_edits = 0
        edits_by_year = {}

        while True:
            post_edits = danbooru_api.post_versions(updater_name=self.name, is_new=False, page=page)
            if not post_edits:
                break
            for post_edit in post_edits:
                try:
                    edits_by_year[post_edit.updated_at.year] += 1
                except KeyError:
                    edits_by_year[post_edit.updated_at.year] = 1

                for tag in post_edit.added_tags:
                    try:
                        data[tag]["added"] += 1
                    except KeyError:
                        data[tag] = {"added": 1, "removed": 0, "revert_added": 0, "revert_removed": 0}
                for tag in post_edit.removed_tags:
                    try:
                        data[tag]["removed"] += 1
                    except KeyError:
                        data[tag] = {"added": 0, "removed": 1, "revert_added": 0, "revert_removed": 0}
                for tag in post_edit.obsolete_added_tags_arr:
                    try:
                        data[tag]["revert_added"] += 1
                    except KeyError:
                        data[tag] = {"added": 0, "removed": 0, "revert_added": 1, "revert_removed": 0}
                for tag in post_edit.obsolete_removed_tags_arr:
                    try:
                        data[tag]["revert_removed"] += 1
                    except KeyError:
                        data[tag] = {"added": 0, "removed": 0, "revert_added": 0, "revert_removed": 1}
            page += 1
            total_edits += len(post_edits)

        logger.info("Done")

        real_edit_url = f"https://danbooru.donmai.us/post_versions?search[updater_name]={self.safe_name}&search[is_new]=false"

        self.post_edit_details = "Actual edits: " + f"{total_edits:_}. Url: <c>{real_edit_url}</c>" + "\n"
        self.post_edit_details += "Top 10 tags changed: " + "\n"
        for tag, counts in sorted(data.items(), key=lambda x: x[1]["added"] + x[1]["removed"], reverse=True)[:10]:
            perc_added_reverted = counts["revert_added"] / counts["added"] if counts["added"] else 0
            arc = "RED" if perc_added_reverted > 0.1 and counts["added"] > 0 else "GREEN"
            perc_added_string = f"<{arc}> {counts['revert_added']} reverted, {perc_added_reverted*100:.2f}% </>"
            self.post_edit_details += f"- {tag}: {counts['added']} added ({perc_added_string}), "

            perc_removed_reverted = counts["revert_removed"] / counts["removed"] if counts["removed"] else 0
            rrc = "RED" if perc_removed_reverted > 0.1 and counts["removed"] > 0 else "GREEN"
            perc_removed_string = f"<{rrc}> {counts['revert_removed']} reverted, {perc_removed_reverted*100:.2f}% </>"
            tag_edit_url = f"{real_edit_url}&search[changed_tags]={tag}"

            self.post_edit_details += f"{counts['removed']} removed ({perc_removed_string}). Url: <c>{tag_edit_url}</>" + "\n"

        self.post_edit_details += "\nEdits by year: " + "\n"
        for year, count in sorted(edits_by_year.items(), reverse=True):
            self.post_edit_details += f"- {year}: {count:_}" + "\n"

    def self_presentation(self, raise_on_old: bool = True) -> str:
        if self.last_edit_days_ago > 365 and raise_on_old:
            raise NoRecentEditsError
        if self.level == 35:
            header = f"<{self.level_color}> User #{self.id}, {self.name}, {self.level_string} </> - Already promoted to <{self.level_color}> contributor </>."  # noqa: E501
        else:
            potential_level = "Contributor" if self.for_contributor else "Builder"
            potential_color = "bg #ffb671" if self.for_contributor else "bg #702963"

            header = f"<{self.level_color}> User #{self.id}, {self.name}, {self.level_string} </> - candidate for <{potential_color}> {potential_level} </>"  # noqa: E501

        ruc = "GREEN" if self.delete_ratio < BUILDER_MAX_DEL_PERC else "RED"
        tuc = "GREEN" if self.total_uploads > MIN_STANDALONE_UPLOADS else "YELLOW"

        return remove_indent(f"""

            {header}

            Url: <c>{self.url}</c>
            {f"\n            Note: <YELLOW> {notes.get(self.id)} </YELLOW>\n" if notes.get(self.id) else ""}
            Recent Deleted: <c>{self.deleted_url}</c>

            Total Uploads: <{tuc}> {self.total_uploads:_} </>. Recent uploads: <{ruc}> {self.recent_uploads:_} </>. Deleted: {self.recent_deleted_colored} ({self.delete_ratio_colored})

            Total Edits: <c>{self.total_edits:_}</c>. Link: <c>{self.edits_url}</c>

            {self.last_edit_string}

            {self.post_edit_details.replace("\n", "\n            ")}

        """)  # noqa: E501

    @property
    def last_edit_days_ago(self) -> int:
        if not self.last_edit_date:
            self.refresh()
            assert self.last_edit_date

        return max((END_DATE - self.last_edit_date).days, 0)  # avoid showing -1 days for edits made while the bot was running

    @property
    def last_edit_string(self) -> str:
        if self.last_edit_days_ago > 365:
            return f"Last edit: <RED> {self.last_edit_days_ago / 365:.2f} years ago. </RED>"

        if self.last_edit_days_ago > 60:
            return f"Last edit: <YELLOW> {self.last_edit_days_ago // 30} months ago. </YELLOW>"

        return f"<GREEN> Last edit: {self.last_edit_days_ago} days ago. </GREEN>"

    @property
    def recent_deleted_colored(self) -> str:
        if self.recent_deleted == 0:
            delete_color = "WHITE"
        elif self.recent_deleted is None:
            delete_color = "MAGENTA"
        elif self.recent_deleted > CONTRIB_RISKY_DEL_COUNT:
            delete_color = "RED" if self.recent_deleted > CONTRIB_MAX_DEL_COUNT else "YELLOW"
        else:
            delete_color = "GREEN"

        return f"<{delete_color}>{self.recent_deleted if self.recent_deleted is not None else "???":^5}</{delete_color}>"

    @property
    def delete_ratio(self) -> int:
        if self.recent_deleted is None:
            self.refresh()
        if self.recent_uploads == 0:
            return 0
        return (self.recent_deleted / self.recent_uploads) * 100

    @property
    def delete_ratio_colored(self) -> str:
        if self.recent_deleted == 0:
            ratio_color = "WHITE"
        elif self.recent_deleted is None:
            ratio_color = "MAGENTA"
        elif self.delete_ratio > BUILDER_MAX_DEL_PERC:
            ratio_color = "RED"
        elif CONTRIB_MAX_DEL_PERC < self.delete_ratio < BUILDER_MAX_DEL_PERC:
            ratio_color = "YELLOW"
        else:
            ratio_color = "GREEN"

        return f"<{ratio_color}>{f"{self.delete_ratio:>6.2f}" if self.recent_deleted is not None else "  ??? "}% </{ratio_color}>"

    @property
    def level_color(self) -> str:
        return level_color_for(self.level)


def level_color_for(level_number: int) -> str:
    return {
        35: "bg #ffb671",           # contributor
        32: "bg #702963",           # builder
        31: "WHITE",                # platinum
        30: "YELLOW",               # gold
    }.get(level_number, "CYAN")     # member


class NoRecentEditsError(Exception):
    pass


class HTMLUser(Candidate):
    @property
    def html_classes(self) -> str:
        classes = ["user"]
        if self.is_banned:
            classes.append("banned")
        elif self.is_deleted:
            classes.append("deleted")
        classes.append(self.level_string.lower())
        return " ".join(classes)

    @property
    def html_name(self) -> str:
        if self.is_banned:
            return f"{self.name} (BANNED)"
        elif self.is_deleted:
            return f"{self.name} (DELETED)"
        else:
            return self.name

    @property
    def html_sort_ratio(self) -> int:
        return self.delete_ratio if self.recent_uploads else 1000

    @property
    def html_deletion_ratio(self) -> str:
        return f"{self.delete_ratio:.2f}" if self.recent_uploads else "n/a"

    @property
    def html_days_ago(self) -> str:
        days_ago = self.last_edit_days_ago
        if days_ago == 0:
            days_ago_str = "today"
        elif days_ago > 365:
            days_ago_str = f"{days_ago//365} years ago"
        elif days_ago > 30:
            days_ago_str = f"{days_ago//30} months ago"
        else:
            days_ago_str = f"{days_ago} days ago"

        return f"{self.last_edit_date:%Y-%m-%d} ({days_ago_str})"

    @property
    def last_edit_timestamp(self) -> int:
        if not self.last_edit_date:
            self.refresh()
        return int(self.last_edit_date.timestamp())  # type: ignore[union-attr]
