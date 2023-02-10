from dateutil import parser as dt_parser

from danboorutools import logger
from danboorutools.models.url import Url


class GelbooruPost:
    @classmethod
    def from_md5(cls, md5: str) -> "GelbooruPost | None":
        """Search for a post using its md5."""
        from danboorutools.logical.sessions.gelbooru import gelbooru_api  # pylint: disable=import-outside-toplevel

        posts = gelbooru_api.posts([f"md5:{md5}"])
        if not posts:
            return None
        post, = posts
        return post

    def __init__(self, json_data: dict):
        self.json_data = json_data

        self.id: int = json_data["id"]
        self.created_at = dt_parser.parse(json_data["created_at"])
        self.uploader_name: str = json_data["owner"]

        self.tags: list[str] = json_data["tags"].split()
        self.rating: str = json_data["rating"][0]
        self.source = Url.parse(json_data["source"])
        self.title: str = json_data["title"]  # AFAIK unused

        self.url = f"https://gelbooru.com/index.php?page=post&s=view&id={self.id}"
        self.file_url: str = json_data["file_url"]

        from danboorutools.logical.sessions.gelbooru import gelbooru_api  # pylint: disable=import-outside-toplevel
        self.api = gelbooru_api

        self._tags_to_add: set[str] = set()
        self._tags_to_remove: set[str] = set()

    def add_tags(self, tags: list[str], send: bool = False) -> None | bool:
        if (tags_to_remove := [t for t in tags if t.startswith("-")]):
            self.remove_tags(tags_to_remove)
            tags = [t for t in tags if not t.startswith("-")]

        for tag in tags:
            if tag in self.tags:
                continue
            if tag in self._tags_to_remove:
                self._tags_to_remove.remove(tag)
            self._tags_to_add.add(tag)

        if send:
            return self.send_tags()
        return None

    def remove_tags(self, tags: list[str], send: bool = False) -> None | bool:
        tags = [t.removeprefix("-") for t in tags]

        for tag in tags:
            if tag not in self.tags:
                continue
            if tag in self._tags_to_add:
                self._tags_to_add.remove(tag)
            self._tags_to_remove.add(tag)

        if send:
            return self.send_tags()
        return None

    def send_tags(self, dry_run: bool = False) -> bool:
        tags_to_send: list[str] = []

        tags_to_send += self._tags_to_add
        tags_to_send += [f"-{tag}" for tag in self._tags_to_remove]

        self._tags_to_add.clear()
        self._tags_to_remove.clear()

        if tags_to_send:
            printable_tags = ", ".join([f"<r>{t}</r>" if t.startswith("-") else f"<g>{t}</g>" for t in tags_to_send])
            logger.info(f"Updating post <e>{self.url}</e> with tags: {printable_tags}")
            if not dry_run:
                self.api.update(self, tags_to_send)
            return True
        return False
