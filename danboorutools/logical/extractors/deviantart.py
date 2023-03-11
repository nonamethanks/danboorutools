import re

from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.sessions.deviantart import DeviantartSession, DeviantartUserData
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url

title_by_username_base36_id = re.compile(r"^(?P<title>.+)_by_(?P<username>.+)[_-]d(?P<base36_deviation_id>[a-z0-9]+)(?:-\w+)?$")
uid_base36_id = re.compile(r"^[a-f0-9]{32}-d(?P<base36_deviation_id>[a-z0-9]+)$")
base36_uid = re.compile(r"^d(?P<base36_deviation_id>[a-z0-9]{6})-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$")
title_by_username = re.compile(r"^(?P<title>.+)_by_(?P<username>.+)$")
FILENAME_PATTERNS = [title_by_username_base36_id, uid_base36_id, base36_uid, title_by_username]


class DeviantArtUrl(Url):
    session = DeviantartSession()


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


class DeviantArtArtistUrl(ArtistUrl, DeviantArtUrl):
    username: str

    normalize_string = "https://www.deviantart.com/{username}"

    @property
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


class DeviantArtImageUrl(PostAssetUrl, DeviantArtUrl):
    deviation_id: int | None
    title: str | None
    username: str | None

    def parse_filename(self, filename: str) -> None:
        filename = filename.split(".")[0]
        try:
            match = next(match for pattern in FILENAME_PATTERNS if (match := pattern.match(filename)))
        except StopIteration as e:
            raise UnparsableUrl(self.parsed_url) from e

        groups: dict[str, str] = match.groupdict()
        self.title = re.sub(r"_+", " ", groups["title"]).title().replace(" ", "-") if "title" in groups else None
        self.username = groups["username"].replace("_", "-") if "username" in groups else None
        self.deviation_id = int(groups["base36_deviation_id"], 36) if "base36_deviation_id" in groups else None

    @property
    def full_size(self) -> str:
        raise RuntimeError("Can't extract full size.")
        # gotta go through the post. TODO: make .files fallback on post maybe? maybe rewrite .files here?
