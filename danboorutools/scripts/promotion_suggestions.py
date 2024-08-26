from __future__ import annotations

import sys
import termios
import textwrap
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

import click

from danboorutools import logger
from danboorutools.logical.sessions.danbooru import danbooru_api, kwargs_to_include

if TYPE_CHECKING:
    from danboorutools.models.danbooru import DanbooruUser

f_path = logger.log_to_file()

END_DATE = datetime.now(tz=UTC)
START_DATE = END_DATE - timedelta(days=60)

MIN_CONTRIBUTOR_UPLOADS_IN_RANGE = 20
MIN_UPLOADS_WITH_EDITS = 500
MIN_STANDALONE_UPLOADS = 700
MIN_EDITS_WITH_UPLOADS = 3000
MIN_STANDALONE_EDITS = 5000
CONTRIB_RISKY_DEL_COUNT = 30
CONTRIB_MAX_DEL_COUNT = 50
CONTRIB_MAX_DEL_PERC = 5
BUILDER_MAX_DEL_PERC = 15


@click.command()
@click.option("--manual", "-m", is_flag=True, show_default=True, default=False)
def main(manual: bool = False) -> None:
    logger.info("Gathering data...")

    recent_uploaders = get_recent_uploaders()

    biggest_uploaders = get_biggest_non_contributor_uploaders()
    biggest_gardeners = get_biggest_non_builder_gardeners()

    candidates: list[Candidate] = []

    for uploader in recent_uploaders:
        if (match := biggest_uploaders.get(uploader.name)):
            merge_candidate(uploader, match)
            candidates.append(uploader)

        elif (match := biggest_gardeners.pop(uploader.name, None)):
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
    if biggest_gardeners.values():
        for match in biggest_gardeners.values():
            # remaining gardeners that weren't caught with the previous pop
            if match.post_update_count > MIN_STANDALONE_EDITS:
                candidate = Candidate(
                    name=match.name,
                    recent_uploads=None,
                    recent_deleted=None,
                )
                merge_candidate(candidate, match)
                remaining.append(candidate)

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
        candidates.sort(key=lambda c: c.total_uploads, reverse=True)
        manual_loop(*candidates)


def manual_loop(*candidates: Candidate) -> None:
    index = 0
    while True:
        candidate = candidates[index]
        logger.info(f"Candidate {index + 1} of {len(candidates)}:")
        logger.info(candidate.self_presentation)
        logger.info(f"{len(candidates) - index - 1} candidates left.")

        while True:
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            logger.info("[N]ext / [P]rev")
            if (_input := input("").strip().lower()) in ["", "n"]:
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
                candidate.refresh()
                break
            else:
                logger.error("Invalid output.")


def merge_candidate(candidate: Candidate, user: DanbooruUser) -> None:
    candidate.id = user.id
    candidate.total_uploads = user.post_upload_count
    candidate.total_edits = user.post_update_count
    candidate.level = user.level
    candidate.level_string = user.level_string
    candidate.is_deleted = user.is_deleted
    candidate.is_banned = user.is_banned


def get_recent_uploaders() -> list[Candidate]:
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

    recent_uploaders: list[Candidate] = []

    for uploader_data in recent_uploaders_data:
        name = uploader_data["uploader"]
        recent_uploaders.append(Candidate(
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
            page=page, level="<32",
            is_banned=False,
        )
        if not last_fetched:
            return gardeners
        gardeners |= {user.name: user for user in last_fetched}
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
    id: int | None = None
    level: int | None = None
    level_string: str | None = None

    @property
    def active(self) -> bool:
        if self.is_deleted:   # can also be None
            return False
        if self.is_banned:  # can also be None  # noqa: SIM103
            return False
        return True

    @property
    def for_contributor(self) -> bool:
        return self.active and self.level == 32 and self.recent_uploads > MIN_CONTRIBUTOR_UPLOADS_IN_RANGE

    @property
    def for_builder(self) -> bool:
        return self.active and self.level != 32

    @property
    def url(self) -> str:
        return f"https://danbooru.donmai.us/users/{self.id}"

    @property
    def deleted_url(self) -> str:
        return f"https://danbooru.donmai.us/posts?tags=user:{quote_plus(self.name)}+status:deleted+age:%3C2mo"

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

    def refresh(self) -> None:
        logger.info("Refreshing data...")
        user, = danbooru_api.users(id=self.id)
        merge_candidate(self, user)
        date_tag = f"date:{START_DATE.strftime("%Y-%m-%d")}..{END_DATE.strftime("%Y-%m-%d")}"
        tags = [f"user:{self.name}", date_tag]
        self.recent_uploads = danbooru_api.post_counts(tags=tags)
        self.recent_deleted = danbooru_api.post_counts(tags=[*tags, "status:deleted"])
        logger.info("Refreshed.")

    @property
    def self_presentation(self) -> str:
        if self.level == 35:
            header = f"<{self.level_color}> User #{self.id}, {self.name}, {self.level_string} </> - Already promoted to <{self.level_color}> contributor </>."  # noqa: E501
        else:
            potential_level = "Contributor" if self.for_contributor else "Builder"
            potential_color = "bg #ffb671" if self.for_contributor else "bg #702963"

            header = f"<{self.level_color}> User #{self.id}, {self.name}, {self.level_string} </> - candidate for <{potential_color}> {potential_level} </>"  # noqa: E501

        ruc = "GREEN" if self.delete_ratio < BUILDER_MAX_DEL_PERC else "RED"
        tuc = "GREEN" if self.total_uploads > MIN_STANDALONE_UPLOADS else "YELLOW"

        return textwrap.dedent(f"""

            {header}

            Url: <c>{self.url}</c>

            Recent Deleted: <c>{self.deleted_url}</c>

            Total Uploads: <{tuc}> {self.total_uploads:_} </>. Recent uploads: <{ruc}> {self.recent_uploads:_} </>. Deleted: {self.recent_deleted_colored} ({self.delete_ratio_colored})

            Total Edits: {self.total_edits:_}.

        """)  # noqa: E501

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
