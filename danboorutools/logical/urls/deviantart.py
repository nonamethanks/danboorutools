from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING

import jwt

from danboorutools.logical.sessions.deviantart import (
    DeviantartHTMLPostData,
    DeviantartPostData,
    DeviantartSession,
    DeviantartUserData,
    ShouldDownloadError,
)
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url

title_by_username_base36_id = re.compile(r"^(?P<title>.+)_by_(?P<username>.+)[_-]d(?P<base36_deviation_id>[a-z0-9]+)(?:-\w+)?$")
uid_base36_id = re.compile(r"^[a-f0-9]{32}-d(?P<base36_deviation_id>[a-z0-9]+)$")
base36_uid = re.compile(r"^d(?P<base36_deviation_id>[a-z0-9]{6})-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$")
title_by_username = re.compile(r"^(?P<title>.+)_by_(?P<username>.+)$")
by_username_base36_id = re.compile(r"^_by_(?P<username>.+)[_-]d(?P<base36_deviation_id>[a-z0-9]+)(?:-\w+)?$")
nothing = re.compile(r"^[a-z0-9]{32}(?:-[a-z0-9]{6})?$")
FILENAME_PATTERNS = [title_by_username_base36_id, uid_base36_id, base36_uid, title_by_username, by_username_base36_id, nothing]

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime


class DeviantArtUrl(Url):
    session = DeviantartSession()


class DeviantArtArtistUrl(ArtistUrl, DeviantArtUrl):
    username: str

    normalize_template = "https://www.deviantart.com/{username}"

    @cached_property
    def artist_data(self) -> DeviantartUserData:
        return self.session.user_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        return [self.username]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls

    def _extract_assets(self) -> list:
        return []

    def _extract_posts_from_each_page(self) -> Iterator[list[DeviantartPostData]]:
        offset = 0
        while True:
            page = self.session.get_posts(self.username, offset)
            yield page.results
            if not page.has_more:
                return
            offset = page.next_offset

    def _process_post(self, post_object: DeviantartPostData) -> None:
        post = DeviantArtPostUrl.parse_and_assert(post_object.url)

        self._register_post(
            post=post,
            assets=post._extract_assets(),
            score=post.score,
            created_at=post.created_at,
        )


class DeviantArtPostUrl(PostUrl, DeviantArtUrl):
    deviation_id: int
    username: str | None
    title: str | None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        deviation_id: int = kwargs["deviation_id"]

        if (username := kwargs.get("username")) and (title := kwargs.get("title")):
            return f"https://www.deviantart.com/{username}/art/{title}-{deviation_id}"
        elif username:
            return f"https://www.deviantart.com/{username}/art/{deviation_id}"
        else:
            return f"https://www.deviantart.com/deviation/{deviation_id}"

    @property
    def post_data(self) -> DeviantartHTMLPostData:
        return self.session.get_post_data(self.deviation_id)

    def _extract_assets(self) -> list[DeviantArtImageUrl]:
        try:
            image = self.post_data.full_size
        except ShouldDownloadError:
            image = self.session.get_download_url(self.post_data.deviation_extended["deviationUuid"])

        return [DeviantArtImageUrl.parse_and_assert(image)]

    @cached_property
    def created_at(self) -> datetime:
        return self.post_data.published_time

    @cached_property
    def score(self) -> int:
        return self.post_data.favorites


class DeviantArtImageUrl(PostAssetUrl, DeviantArtUrl):
    deviation_id: int | None
    title: str | None
    username: str | None

    @property
    def jwt(self) -> dict:
        token = self.parsed_url.query.get("token") or self.parsed_url.query.get("downloadToken")
        if not token:
            return {}
        return jwt.decode(token, options={"verify_signature": False})

    @property
    def jwt_permissions(self) -> dict[str, str]:
        if not self.jwt:
            return {}
        return self.jwt.get("payload") or self.jwt["obj"][0][0]

    @property
    def max_width(self) -> int | None:
        if not self.jwt_permissions:
            return None

        return int(self.jwt_permissions["width"].removeprefix("<="))

    @property
    def max_height(self) -> int | None:
        if not self.jwt_permissions:
            return None

        return int(self.jwt_permissions["height"].removeprefix("<="))

    @staticmethod
    def parse_filename(filename: str) -> tuple[str | None, int | None, str | None]:
        filename = filename.split(".")[0]
        match = next(match for pattern in FILENAME_PATTERNS if (match := pattern.match(filename)))

        groups: dict[str, str] = match.groupdict()
        username = groups["username"].replace("_", "-") if "username" in groups else None
        deviation_id = int(groups["base36_deviation_id"], 36) if "base36_deviation_id" in groups else None
        title = re.sub(r"_+", " ", groups["title"]).title().replace(" ", "-") if "title" in groups else None

        return username, deviation_id, title

    @property
    def full_size(self) -> str:
        url = self.parsed_url.raw_url

        if self.parsed_url.domain != "wixmp.com":
            return url
        elif "/v1/" in self.parsed_url.path:
            if self.deviation_id and self.deviation_id <= 790_677_560 and self.parsed_url.extension != "gif":
                url = f"https://{self.parsed_url.hostname}/intermediary{self.parsed_url.path}"\
                    .replace("intermediary/intermediary", "intermediary")
                return re.sub(r"\/v1\/.*", "", url)
            elif self.max_width is not None and self.max_height is not None:
                sample_options = f"w_{self.max_width},h_{self.max_height}"
                if self.jwt_permissions.get("blur"):
                    sample_options += f",blur_{self.jwt_permissions["blur"]}"

                return re.sub(r"\/v1\/[^\/]+\/[^\/]+\/", f"/v1/fill/{sample_options}/", url)
            else:
                return re.sub(r",q_\d+,strp\/", r"\/", url)
        else:
            return url
