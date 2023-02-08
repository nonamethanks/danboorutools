from typing import Self

from dateutil import parser as dt_parser

from danboorutools.models.file import File
from danboorutools.models.url import Url


class DanbooruModel:
    model_name: str

    def __init__(self, json_data: dict):
        if self.__class__ == DanbooruModel:
            raise RuntimeError("This class cannot be instantiated directly, and must be inherited.")

        from danboorutools.logical import danbooru_api  # pylint: disable=import-outside-toplevel
        self.api = danbooru_api
        self.apply_json_data(json_data)

    def apply_json_data(self, json_data: dict) -> None:
        self.json_data = json_data
        self.id: int = json_data["id"]

        self.updated_at = dt_parser.parse(json_data["updated_at"]) if "updated_at" in json_data else None
        self.created_at = dt_parser.parse(json_data["created_at"]) if "created_at" in json_data else self.updated_at
        self.is_deleted: bool = json_data.get("is_deleted", False)

        for property_name, property_class in self.__annotations__.items():  # pylint: disable=no-member
            if (property_data := json_data.get(property_name)) is not None:
                # if property_class.__origin__ == list:
                #     property_subclass = property_class.__args__[0]
                #     setattr(self, property_name, [property_subclass(prop) for prop in property_data])  # list[str]
                # else:
                setattr(self, property_name, property_class(property_data))
            else:
                setattr(self, property_name, None)

        self.model_path = f"/{self.model_name}s/{self.id}"
        self.url = "https://danbooru.donmai.us" + self.model_path

    def delete(self) -> None:
        self.api.danbooru_request("DELETE", endpoint=self.model_path)

    @classmethod
    def from_id(cls, model_id: int) -> Self:  # type: ignore  # XXX false positive
        from danboorutools.logical import danbooru_api  # pylint: disable=import-outside-toplevel
        json_data = danbooru_api.danbooru_request("GET", f"{cls.model_name}s/{model_id}.json")
        assert isinstance(json_data, dict)
        return cls(json_data)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.url}]"
    __repr__ = __str__

    def refresh(self) -> None:
        new_post = self.from_id(self.id)
        self.apply_json_data(new_post.json_data)  # type: ignore # XXX false positive


class DanbooruPost(DanbooruModel):
    model_name = "post"

    score: int
    md5: str

    @property
    def source(self) -> Url:
        return Url.parse(self.json_data["source"])

    def apply_json_data(self, json_data: dict) -> None:
        super().apply_json_data(json_data)
        self.tags: list[str] = json_data["tag_string"].split()
        self.character_tags: list[str] = json_data["tag_string_character"].split()
        self.copyright_tags: list[str] = json_data["tag_string_copyright"].split()
        self.artist_tags: list[str] = json_data["tag_string_artist"].split()
        self.meta_tags: list[str] = json_data["tag_string_meta"].split()

    def replace(self,
                replacement_url: Url | None = None,
                replacement_file: File | None = None,
                final_source: Url | None = None,
                refresh: bool = False
                ) -> None:
        if not replacement_file:
            replacement_url = replacement_url or self.source
        self.api.replace(self, replacement_url=replacement_url, replacement_file=replacement_file,
                         final_source=final_source or replacement_url)
        if refresh:
            self.refresh()


class DanbooruUser(DanbooruModel):
    model_name = "user"

    name: str
    level: int
    level_string: str
    post_update_count: int
    note_update_count: int
    post_upload_count: int
    is_banned: bool

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.name}]"


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

    def apply_json_data(self, json_data: dict) -> None:
        super().apply_json_data(json_data)
        self.obsolete_removed_tags: list[str] = json_data["obsolete_removed_tags"].split()
        self.obsolete_added_tags: list[str] = json_data["obsolete_added_tags"].split()


class DanbooruArtist(DanbooruModel):
    name: str
    group_name: str
    is_banned: bool
    other_names: list[str]


class DanbooruWikiPage(DanbooruModel):
    title: str
    body: str
    is_locked: bool
    other_names: list[str]


class DanbooruTag(DanbooruModel):
    name: str
    post_count: int
    category: int
    artist: DanbooruArtist
    is_deprecated: bool
    wiki_page: DanbooruWikiPage
