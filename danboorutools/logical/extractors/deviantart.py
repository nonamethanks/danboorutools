import re

from danboorutools.exceptions import UnparsableUrl
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url

title_by_username_base36_id = re.compile(r"^(?P<title>.+)_by_(?P<username>.+)[_-]d(?P<base36_deviation_id>[a-z0-9]+)(?:-\w+)?$")
uid_base36_id = re.compile(r"^[a-f0-9]{32}-d(?P<base36_deviation_id>[a-z0-9]+)$")
base36_uid = re.compile(r"^d(?P<base36_deviation_id>[a-z0-9]{6})-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$")
title_by_username = re.compile(r"^(?P<title>.+)_by_(?P<username>.+)$")
FILENAME_PATTERNS = [title_by_username_base36_id, uid_base36_id, base36_uid, title_by_username]


class DeviantArtUrl(Url):
    pass


class DeviantArtPostUrl(PostUrl, DeviantArtUrl):
    normalization = "https://www..deviantart.com/{artist_name}/art/{title}-{deviation_id}"

    deviation_id: int
    username: str | None
    title: str | None

    @classmethod
    def _normalize_from_properties(cls, **kwargs) -> str:
        deviation_id: int = kwargs["deviation_id"]
        username: str | None = kwargs.get("username")
        title: str | None = kwargs.get("title")

        if username and title:
            return f"https://www.deviantart.com/{username}/art/{title}-{deviation_id}"
        else:
            return f"https://deviantart.com/deviation/{deviation_id}"


class DeviantArtArtistUrl(ArtistUrl, DeviantArtUrl):
    normalization = "https://www.deviantart.com/{artist_name}"
    username: str


class DeviantArtImageUrl(PostAssetUrl, DeviantArtUrl):
    deviation_id: int | None
    title: str | None
    username: str | None

    def parse_filename(self, filename: str) -> None:
        filename = filename.split(".")[0]
        try:
            match = next(match for pattern in FILENAME_PATTERNS if (match := pattern.match(filename)))
        except StopIteration as e:
            raise UnparsableUrl(self.original_url) from e

        groups: dict[str, str] = match.groupdict()
        self.title = re.sub(r"_+", " ", groups["title"]).title().replace(" ", "-") if "title" in groups else None
        self.username = groups["username"].replace("_", "-") if "username" in groups else None
        self.deviation_id = int(groups["base36_deviation_id"], 36) if "base36_deviation_id" in groups else None


class FavMeUrl(RedirectUrl):
    # TODO: this doesn't need to do a redirection, it can be converted to a DeviantArtImageUrl which can then fetch the post as required
    favme_id: str
