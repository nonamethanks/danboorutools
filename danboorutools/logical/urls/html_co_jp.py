from functools import cached_property

from danboorutools.models.url import InfoUrl, Url


class HtmlCoJpArtistUrl(InfoUrl, Url):
    username: str

    normalize_template = "https://html.co.jp/zeelch"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []

    @cached_property
    def is_deleted(self) -> bool:
        return True
