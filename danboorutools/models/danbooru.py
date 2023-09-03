from __future__ import annotations

import re
from datetime import datetime
from functools import cached_property
from typing import ClassVar, Self

from pydantic import validator

from danboorutools.exceptions import NotAnUrlError
from danboorutools.models.file import File
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel

CATEGORY_MAP = {
    0: "general",
    4: "character",
    3: "copyright",
    1: "artist",
    5: "meta",
}


class DanbooruModel(BaseModel):
    id: int  # noqa: A003
    created_at: datetime | None
    updated_at: datetime | None
    is_deleted: bool = False

    model_name: ClassVar[str | None] = None

    @property
    def model_path(self) -> str:
        try:
            return f"{self.model_name}s/{self.id}"
        except AttributeError as e:
            raise NotImplementedError from e

    @property
    def url(self) -> str:
        if self.model_path:
            return f"https://danbooru.donmai.us/{self.model_path}"
        raise NotImplementedError

    def delete(self) -> None:
        from danboorutools.logical.sessions.danbooru import danbooru_api
        danbooru_api.danbooru_request("DELETE", endpoint=self.model_path)

    @classmethod
    def from_id(cls, model_id: int) -> Self:
        from danboorutools.logical.sessions.danbooru import danbooru_api
        json_data = danbooru_api.danbooru_request("GET", f"{cls.model_name}s/{model_id}.json")
        assert isinstance(json_data, dict)
        assert json_data["id"] == model_id
        return cls(**json_data)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.url}]"
    __repr__ = __str__

    @classmethod
    def id_from_url(cls, url: str) -> int:
        if not cls.model_name:
            raise NotImplementedError

        match = re.search(rf"donmai\.us\/{cls.model_name}(s|\/show)\/(?P<id>\d+)", url)
        try:
            assert match
            return int(match.groupdict()["id"])  # noqa: TRY300
        except Exception as e:
            e.add_note(f"Url: {url}")
            e.add_note(f"Match: {match}")
            raise


class DanbooruPost(DanbooruModel):
    model_name = "post"

    score: int
    md5: str
    file_ext: str
    file_url: str

    tag_string: str
    tag_string_character: str
    tag_string_copyright: str
    tag_string_artist: str
    tag_string_meta: str

    @property
    def source(self) -> Url | str:
        try:
            return Url.parse(self._raw_data["source"])
        except NotAnUrlError:
            return self._raw_data["source"]

    @property
    def tags(self) -> list[str]:
        return self.tag_string.split()

    @property
    def character_tags(self) -> list[str]:
        return self.tag_string_character.split()

    @property
    def copyright_tags(self) -> list[str]:
        return self.tag_string_copyright.split()

    @property
    def artist_tags(self) -> list[str]:
        return self.tag_string_artist.split()

    @property
    def meta_tags(self) -> list[str]:
        return self.tag_string_meta.split()

    def replace(self,
                replacement_url: Url | str | None = None,
                replacement_file: File | None = None,
                final_source: Url | None = None,
                ) -> None:
        from danboorutools.logical.sessions.danbooru import danbooru_api
        if not replacement_file:
            replacement_url = replacement_url or self.source
        danbooru_api.replace(self, replacement_url=replacement_url, replacement_file=replacement_file,
                             final_source=final_source or replacement_url)

    @property
    def file(self) -> File:
        raise NotImplementedError

    @property
    def is_animated(self) -> bool:
        return "animated" in self.tags or "video" in self.tags or self.file_ext == "swf"


class DanbooruIqdbMatch(DanbooruModel):
    post: DanbooruPost
    score: float


class DanbooruUser(DanbooruModel):
    model_name = "user"

    name: str
    level: int
    level_string: str
    post_update_count: int
    note_update_count: int
    post_upload_count: int
    is_banned: bool


class DanbooruComment(DanbooruModel):
    model_name = "comment"

    user: DanbooruUser
    post: DanbooruPost


class DanbooruPostVote(DanbooruModel):
    model_name = "post_vote"

    post: DanbooruPost
    user: DanbooruUser
    score: int


class DanbooruCommentVote(DanbooruModel):
    model_name = "comment_vote"

    comment: DanbooruComment
    user: DanbooruUser
    score: int


class DanbooruPostVersion(DanbooruModel):
    model_name = "post_version"

    updater: DanbooruUser
    post: DanbooruPost

    added_tags: list[str]
    removed_tags: list[str]

    @property
    def url(self) -> str:
        return f"https://danbooru.donmai.us/post_versions?search[id]={self.id}"


class DanbooruArtist(DanbooruModel):
    model_name = "artist"

    name: str
    is_banned: bool
    other_names: list[str]
    tag: DanbooruTag

    @property
    def urls(self) -> list[Url]:
        urls = []
        for url_data in self._raw_data["urls"]:
            url = Url.parse(url_data["url"])
            # url.is_deleted = not url_data["is_active"]
            urls.append(url)
        return urls


class DanbooruWikiPage(DanbooruModel):
    model_name = "wiki_page"

    title: str
    body: str
    is_locked: bool
    other_names: list[str]


class DanbooruTag(DanbooruModel):
    model_name = "tag"

    name: str
    post_count: int
    category: int
    is_deprecated: bool

    @property
    def category_name(self) -> str:
        return CATEGORY_MAP[self.category]

    @property
    def artist(self) -> DanbooruArtist:
        if "artist" in self._raw_data:
            return DanbooruArtist(**self._raw_data["artist"])
        raise NotImplementedError  # cache?

    @property
    def wiki_page(self) -> DanbooruWikiPage:
        if "wiki_page" in self._raw_data:
            return DanbooruWikiPage(**self._raw_data["wiki_page"])
        raise NotImplementedError  # cache?


class DanbooruUserEvent(DanbooruModel):
    model_name = "user_event"

    category: str
    user_session: DanbooruUserSession
    user: DanbooruUser


class DanbooruUserSession(DanbooruModel):
    model_name = "user_session"

    ip_addr: str
    session_id: str
    user_agent: str


class DanbooruBan(DanbooruModel):
    model_name = "ban"

    reason: str
    duration: int

    user: DanbooruUser
    banner: DanbooruUser


DanbooruArtist.update_forward_refs()
DanbooruUserEvent.update_forward_refs()
