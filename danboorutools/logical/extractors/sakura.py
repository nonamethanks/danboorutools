from functools import cached_property

from danboorutools.exceptions import HTTPError
from danboorutools.models.url import ArtistUrl, Url


class SakuraUrl(Url):
    blog_name: str


class SakuraBlogUrl(ArtistUrl, SakuraUrl):
    # normalize_template = "http://{blog_name}.sakura.ne.jp"  # what about all those random folders?
    # http://www17t.sakura.ne.jp/~room121/ etc

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return None

    @cached_property
    def is_deleted(self) -> bool:
        try:
            return "このサーバーは、さくらのレンタルサーバで提供されています。" in self.html
        except HTTPError as e:
            if e.status_code == 403:
                return True
            else:
                assert e.response
                return "このサーバーは、さくらのレンタルサーバで提供されています。" in e.response.text
        except ConnectionError as e:
            if "Name or service not known" in str(e):
                return True
            raise
