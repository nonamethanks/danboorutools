from functools import cached_property

from danboorutools.logical.sessions.circle_ms import CircleMsSession
from danboorutools.models.url import InfoUrl, Url


class CircleMsUrl(Url):
    session = CircleMsSession()


class CircleMsCircleUrl(InfoUrl, CircleMsUrl):
    circle_id: int

    normalize_template = "https://portal.circle.ms/Circle/Index/{circle_id}"

    @cached_property
    def is_deleted(self) -> bool:
        if "※検索キーワードを入力してください" in str(self.html):
            return True
        elif "このサークルは見つかりません" in str(self.html):
            return True
        elif "は非公開設定にしています。" in str(self.html):
            return True  # private, but p much same thing
        elif self.html.select_one(".profile-name"):
            return False
        else:
            raise NotImplementedError(f"Couldn't check state of {self}, cookie might be out of date.")

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        return [self.html.select_one(".profile-name").text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        return [Url.parse(el["href"]) for el in self.html.select(".profile-link a")]
