import time

from dateutil import parser as dt_parser


class GelbooruPost:
    def __init__(self, json_data: dict):
        self.json_data = json_data

        self.id: int = json_data["id"]
        self.created_at = dt_parser.parse(json_data["created_at"])
        self.uploader_name: str = json_data["owner"]

        self.tags: list[str] = json_data["tags"].split()
        self.rating: str = json_data["rating"][0]
        self.source: str = json_data["source"]

        self.url = f"https://gelbooru.com/index.php?page=post&s=view&id={self.id}"
        self.file_url: str = json_data["file_url"]

        from danboorutools.logical import gelbooru_api  # pylint: disable=import-outside-toplevel
        self.gelbooru_api = gelbooru_api

    def update(self, tags: list[str], rating: str | None = None) -> None:
        if rating:
            assert len(rating) == 1

        final_tags = self.tags + [t for t in tags if not t.startswith("-")]
        final_tags = [t for t in final_tags if "-" + t not in tags]

        first_request = self.gelbooru_api.gelbooru_request("GET", f"/index.php?page=post&s=view&id={self.id}")
        token = self.gelbooru_api.get_csrf(first_request)

        payload = {
            "csrf-token": token,
            "id": self.id,
            "lupdated": int(time.time()),
            "pconf": 1,
            "rating": rating or self.rating,
            "source": self.source,
            "submit": "Save changes",
            "tags": " ".join(final_tags),
            "title": "",
            "uid": self.gelbooru_api.config_user_id,
            "uname": self.gelbooru_api.config_username,
        }

        if ">Unlock Image</a>" in first_request.text:
            self.unlock(token)

        self.gelbooru_api.gelbooru_request("POST", "/public/edit_post.php", data=payload)

    def unlock(self, token: str) -> None:
        lock_url = f"/public/lock.php?id={self.id}&csrf-token={token}"
        self.gelbooru_api.gelbooru_request("GET", lock_url)
