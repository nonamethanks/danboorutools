import re

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class NewgroundsUrl(Url):
    pass


class NewgroundsPostUrl(PostUrl, NewgroundsUrl):
    username: str
    title: str

    normalize_string = "https://www.newgrounds.com/art/view/{username}/{title}"


class NewgroundsDumpUrl(PostUrl, NewgroundsUrl):
    dump_id: str

    normalize_string = "https://www.newgrounds.com/dump/item/{dump_id}"


class NewgroundsVideoPostUrl(PostUrl, NewgroundsUrl):
    video_id: int

    normalize_string = "https://www.newgrounds.com/portal/view/{video_id}"


class NewgroundsArtistUrl(ArtistUrl, NewgroundsUrl):
    username: str

    normalize_string = "https://{username}.newgrounds.com"


class NewgroundsAssetUrl(PostAssetUrl, NewgroundsUrl):
    username: str | None
    title: str | None

    @property
    def full_size(self) -> str:
        if self.parsed_url.hostname == "uploads.ungrounded.net":
            return re.sub(r"\.\d+p\.", ".", self.parsed_url.url_without_query)
        elif self.parsed_url.url_parts[0] in ("images", "comments"):
            return self.parsed_url.url_without_query
        else:
            raise NotImplementedError
