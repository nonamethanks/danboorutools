from __future__ import annotations

import re
from datetime import datetime
from typing import ClassVar, Self

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
    id: int
    created_at: datetime | None
    updated_at: datetime | None = None
    is_deleted: bool = False

    danbooru_model_name: ClassVar[str | None] = None

    @property
    def model_path(self) -> str:
        try:
            return f"{self.danbooru_model_name}s/{self.id}"
        except AttributeError as e:
            raise NotImplementedError from e

    @property
    def url(self) -> str:
        if self.model_path:
            return f"https://danbooru.donmai.us/{self.model_path}"
        raise NotImplementedError

    def delete(self) -> None:
        from danboorutools.logical.sessions.danbooru import DanbooruApi
        admin_api = DanbooruApi(domain="danbooru", mode="main")
        admin_api.danbooru_request("DELETE", endpoint=self.model_path + ".json")

    @classmethod
    def get_from_id(cls, model_id: int) -> Self:
        from danboorutools.logical.sessions.danbooru import danbooru_api
        json_data = danbooru_api.danbooru_request("GET", f"{cls.danbooru_model_name}s/{model_id}.json")
        assert isinstance(json_data, dict)
        assert json_data["id"] == model_id
        return cls(**json_data)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.url}]"
    __repr__ = __str__

    @classmethod
    def id_from_url(cls, url: str) -> int:
        if not cls.danbooru_model_name:
            raise NotImplementedError

        match = re.search(rf"donmai\.us\/{cls.danbooru_model_name}(s|\/show)\/(?P<id>\d+)", url)
        try:
            assert match
            return int(match.groupdict()["id"])
        except Exception as e:
            e.add_note(f"Url: {url}")
            e.add_note(f"Match: {match}")
            raise

    def __hash__(self):
        return hash(self.url)


class DanbooruMediaAsset(DanbooruModel):
    danbooru_model_name = "media_asset"

    md5: str
    pixel_hash: str

    file_ext: str
    image_height: int
    image_width: int
    file_size: int

    duration: float | None

    variants: list[dict]


class DanbooruPost(DanbooruModel):
    danbooru_model_name = "post"

    is_pending: bool

    score: int
    uploader_id: int

    tag_string: str
    tag_string_character: str
    tag_string_copyright: str
    tag_string_artist: str
    tag_string_meta: str

    media_asset: DanbooruMediaAsset

    @property
    def is_active(self) -> bool:
        return not self.is_deleted and not self.is_pending

    @property
    def md5(self) -> str:
        return self.media_asset.md5

    @property
    def file_ext(self) -> str:
        return self.media_asset.file_ext

    @property
    def file_url(self) -> str:
        return next(filter(lambda x: x["type"] == "original", self.media_asset.variants))["url"]

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


class DanbooruIqdbMatch(BaseModel):
    post: DanbooruPost
    score: float


class DanbooruUser(DanbooruModel):
    danbooru_model_name = "user"

    name: str
    level: int
    level_string: str
    post_update_count: int
    note_update_count: int
    post_upload_count: int
    is_banned: bool


class DanbooruComment(DanbooruModel):
    danbooru_model_name = "comment"

    post: DanbooruPost
    creator: DanbooruUser

    body: str
    score: int


class DanbooruPostVote(DanbooruModel):
    danbooru_model_name = "post_vote"

    post: DanbooruPost
    user: DanbooruUser
    score: int


class DanbooruCommentVote(DanbooruModel):
    danbooru_model_name = "comment_vote"

    comment: DanbooruCommentForVote
    user: DanbooruUser
    score: int


class DanbooruCommentForVote(DanbooruModel):
    danbooru_model_name = "comment"

    user: DanbooruUser | None = None
    user_id: int | None = None
    post: DanbooruPost | None = None
    post_id: int | None = None


class DanbooruForumTopic(DanbooruModel):
    danbooru_model_name = "forum_topic"

    title: str
    is_sticky: bool
    is_locked: bool

    min_level: int
    category_id: int


class DanbooruForumPost(DanbooruModel):
    danbooru_model_name = "forum_post"

    creator: DanbooruUser
    topic: DanbooruForumTopic

    body: str


class DanbooruFlag(DanbooruModel):
    danbooru_model_name = "post_flag"

    post: DanbooruPost
    creator: DanbooruUser | None = None

    reason: str
    status: str
    category: str
    is_resolved: bool


class DanbooruAppeal(DanbooruModel):
    danbooru_model_name = "post_appeal"

    post: DanbooruPost
    creator: DanbooruUser

    reason: str
    status: str


class DanbooruPostVersion(DanbooruModel):
    danbooru_model_name = "post_version"

    updater: DanbooruUser
    post: DanbooruPost

    added_tags: list[str]
    removed_tags: list[str]

    obsolete_added_tags: str
    obsolete_removed_tags: str

    created_at: datetime | None = None

    @property
    def url(self) -> str:
        return f"https://danbooru.donmai.us/post_versions?search[id]={self.id}"

    @property
    def obsolete_added_tags_arr(self) -> list[str]:
        return self.obsolete_added_tags.split(" ")

    @property
    def obsolete_removed_tags_arr(self) -> list[str]:
        return self.obsolete_removed_tags.split(" ")

    @property
    def tags_after_edit(self) -> list[str]:
        return sorted((set(self.added_tags) | set(self.post.tags)) - set(self.removed_tags))

    @property
    def tags_before_edit(self) -> list[str]:
        return sorted((set(self.removed_tags) | set(self.post.tags)) - set(self.added_tags))


class DanbooruArtist(DanbooruModel):
    danbooru_model_name = "artist"

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


class DanbooruBulkUpdateRequest(DanbooruModel):
    danbooru_model_name = "bulk_update_request"

    user_id: int
    forum_topic_id: int | None  # this is what happens when someone removes a BUR from a topic ORZ
    forum_post_id: int | None  # this is what happens when someone removes a BUR from a topic ORZ
    script: str
    status: str
    approver_id: int | None = None
    tags: list[str]


class DanbooruWikiPage(DanbooruModel):
    danbooru_model_name = "wiki_page"

    title: str
    body: str
    is_locked: bool
    other_names: list[str]

    def get_linked_tags(self, pattern: re.Pattern | str | None = None) -> list[str]:
        pattern = re.compile(pattern or r"\[\[([^|\[\]]+)(?:\|(.*))?\]\]")

        tags = [t[0].strip() for t in pattern.findall(self.body)]
        return [t.replace(" ", "_").lower() for t in tags]


class DanbooruTag(DanbooruModel):
    danbooru_model_name = "tag"

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


class DanbooruTagImplication(DanbooruModel):
    danbooru_model_name = "tag_implication"

    reason: str
    creator: DanbooruUser
    approver: DanbooruUser | None = None

    antecedent_tag: DanbooruTag
    consequent_tag: DanbooruTag


class DanbooruUserEvent(DanbooruModel):
    danbooru_model_name = "user_event"

    category: str
    user_session: DanbooruUserSession
    user: DanbooruUser


class DanbooruUserSession(DanbooruModel):
    danbooru_model_name = "user_session"

    ip_addr: str
    session_id: str
    user_agent: str


class DanbooruBan(DanbooruModel):
    danbooru_model_name = "ban"

    reason: str
    duration: int

    user: DanbooruUser
    banner: DanbooruUser


class DanbooruDmail(DanbooruModel):
    danbooru_model_name = "dmail"

    from_id: int
    to_id: int

    title: str
    body: str

    is_read: bool
    is_deleted: bool
    is_spam: bool

    key: str


class DanbooruFeedback(DanbooruModel):
    danbooru_model_name = "user_feedback"

    body: str
    category: str

    user: DanbooruUser
    creator: DanbooruUser


class DanbooruReplacement(DanbooruModel):
    danbooru_model_name = "post_replacement"

    post: DanbooruPost


DanbooruArtist.model_rebuild(force=True)
DanbooruUserEvent.model_rebuild(force=True)
