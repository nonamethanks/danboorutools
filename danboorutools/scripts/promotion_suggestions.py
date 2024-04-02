from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

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


def main() -> None:
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

    logger.info("Contributor candidates:")
    for candidate in [c for c in candidates if c.level == 32 and c.recent_uploads > MIN_CONTRIBUTOR_UPLOADS_IN_RANGE and c.active]:
        logger.info(candidate.self_string)

    logger.info("")
    logger.info("Builder/Contributor candidates:")

    for candidate in [c for c in candidates if c.level != 32 and c.active]:
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

    if remaining:
        logger.info("Builder candidates:")
        for candidate in [c for c in remaining if c.level != 32 and c.active]:
            logger.info(candidate.self_string)


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
            recent_deleted=deleted_map.get(name)),
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
        if self.is_banned:  # can also be None
            return False
        return True

    @property
    def url(self) -> str:
        return f"https://danbooru.donmai.us/users/{self.id}"

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

        if not self.delete_ratio:
            ratio_color = "WHITE"
        elif self.delete_ratio > BUILDER_MAX_DEL_PERC:
            ratio_color = "RED"
        elif CONTRIB_MAX_DEL_PERC < self.delete_ratio < BUILDER_MAX_DEL_PERC:
            ratio_color = "YELLOW"
        else:
            ratio_color = "GREEN"

        if not self.recent_deleted:
            delete_color = "WHITE"
        elif self.recent_deleted > CONTRIB_RISKY_DEL_COUNT:
            delete_color = "RED" if self.recent_deleted > CONTRIB_MAX_DEL_COUNT else "YELLOW"
        else:
            delete_color = "GREEN"

        if not (self.recent_deleted is None and self.recent_uploads is None):
            delete_string = f"<{delete_color}>{self.recent_deleted if self.recent_deleted is not None else "???":^5}</{delete_color}>"
            if self.delete_ratio is not None:
                ratio_string = f"<{ratio_color}>{self.delete_ratio:>6.2f} </{ratio_color}> %"
            else:
                ratio_string = f"<{ratio_color}>{"???":>6} </{ratio_color}> %"
            string += f"{self.recent_uploads if self.recent_uploads is not None else "???":>6} / {delete_string} = {ratio_string} | "

        string += f" {self.url}"

        return string

    @property
    def delete_ratio(self) -> int:
        if self.recent_deleted is None:
            return None
        return (self.recent_deleted / self.recent_uploads) * 100

    @property
    def level_color(self) -> str:
        if self.level == 32:
            level_color = "bg #702963"
        elif self.level == 31:
            level_color = "WHITE"
        elif self.level == 30:
            level_color = "YELLOW"
        else:
            level_color = "CYAN"
        return level_color
