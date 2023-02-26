import re

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class NewgroundsUrl(Url):
    pass


class NewgroundsPostUrl(PostUrl, NewgroundsUrl):
    username: str
    title: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.newgrounds.com/art/view/{kwargs['username']}/{kwargs['title']}"


class NewgroundsDumpUrl(PostUrl, NewgroundsUrl):
    dump_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        # TODO: need to separate this and dump download url, which is the asset
        return f"https://www.newgrounds.com/dump/item/{kwargs['dump_id']}"


class NewgroundsVideoPostUrl(PostUrl, NewgroundsUrl):
    video_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.newgrounds.com/portal/view/{kwargs['video_id']}"


class NewgroundsArtistUrl(ArtistUrl, NewgroundsUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://{kwargs['username']}.newgrounds.com"


class NewgroundsAssetUrl(PostAssetUrl, NewgroundsUrl):
    username: str | None
    title: str | None

    @property
    def full_size(self) -> str:
        if self.parsed_url.hostname == "uploads.ungrounded.net":
            return re.sub(r"\.\d+p\.", ".", self.parsed_url.url_without_params)
        elif self.parsed_url.url_parts[0] in ("images", "comments"):
            return self.parsed_url.url_without_params
        else:
            raise NotImplementedError
