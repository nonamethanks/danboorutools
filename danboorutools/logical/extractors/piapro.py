from typing import Literal

from danboorutools.models.url import ArtistUrl, PostUrl, Url


class PiaproUrl(Url):
    pass


class PiaproArtistUrl(ArtistUrl, PiaproUrl):
    username: str

    normalize_template = "https://piapro.jp/{username}"

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        return [self.html.select_one("#user_prof > p > span").text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        return [Url.parse(a["href"]) for a in self.html.select(".prof_sns_list_wrap a")]


class PiaproPostUrl(PostUrl, PiaproUrl):
    post_id: str
    post_type: Literal["t", "content"]

    normalize_template = "https://piapro.jp/{post_type}/{post_id}"
