import binascii
import re

from danboorutools.logical.sessions.deviantart import DeviantartSession, DeviantartUserData
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url

title_by_username_base36_id = re.compile(r"^(?P<title>.+)_by_(?P<username>.+)[_-]d(?P<base36_deviation_id>[a-z0-9]+)(?:-\w+)?$")
uid_base36_id = re.compile(r"^[a-f0-9]{32}-d(?P<base36_deviation_id>[a-z0-9]+)$")
base36_uid = re.compile(r"^d(?P<base36_deviation_id>[a-z0-9]{6})-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$")
title_by_username = re.compile(r"^(?P<title>.+)_by_(?P<username>.+)$")
by_username_base36_id = re.compile(r"^_by_(?P<username>.+)[_-]d(?P<base36_deviation_id>[a-z0-9]+)(?:-\w+)?$")
nothing = re.compile(r"^[a-z0-9]{32}(?:-[a-z0-9]{6})?$")
FILENAME_PATTERNS = [title_by_username_base36_id, uid_base36_id, base36_uid, title_by_username, by_username_base36_id, nothing]


class DeviantArtUrl(Url):
    session = DeviantartSession()


class DeviantArtPostUrl(PostUrl, DeviantArtUrl):
    deviation_id: int
    username: str | None
    title: str | None

    uuid: str | None = None  # useful to avoid api calls

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

    normalize_template = "https://www.deviantart.com/{username}"

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
        raise RuntimeError("Can't extract full size.")
        # gotta go through the post. TODO: make .files fallback on post maybe? maybe rewrite .files here?

    @staticmethod
    def _extract_best_image(image_sample: str) -> str:
        # https://github.com/mikf/gallery-dl/commit/02a247f4e54b6835e81102b84583bdae0969a050#commitcomment-58578639
        url, sep, _ = image_sample.partition("/v1/")
        if not sep:
            return image_sample

        payload = (
            b'{"sub":"urn:app:","iss":"urn:app:","obj":[[{"path":"/f/' +
            url.partition("/f/")[2].encode() +
            b'"}]],"aud":["urn:service:file.download"]}'
        )

        return (
            "{}?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.{}.".format(
                url,
                #  base64 of 'header' is precomputed as 'eyJ0eX...'
                #  binascii.a2b_base64(header).rstrip(b"=\n").decode(),
                binascii.b2a_base64(payload).rstrip(b"=\n").decode())
        )
