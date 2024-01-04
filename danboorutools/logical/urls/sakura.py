from functools import cached_property

from danboorutools.exceptions import HTTPError
from danboorutools.models.url import ArtistUrl, Url


class SakuraUrl(Url):
    blog_name: str


class SakuraBlogUrl(ArtistUrl, SakuraUrl):

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        # http://www17t.sakura.ne.jp/~room121/
        # http://warden.x0.com
        # not really normalizable
        return None

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.blog_name]

    @property
    def related(self) -> list[Url]:
        return []

    @cached_property
    def is_deleted(self) -> bool:
        try:
            return "このサーバーは、さくらのレンタルサーバで提供されています。" in self.html
        except HTTPError as e:
            if e.status_code == 403:
                return True

            if e.response:
                return "このサーバーは、さくらのレンタルサーバで提供されています。" in e.response.text

            if e.status_code == 0:  # name resolution error etc
                return True

            raise NotImplementedError from e
