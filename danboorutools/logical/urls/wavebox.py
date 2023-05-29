import re

from danboorutools.models.url import InfoUrl, Url


class WaveboxUrl(InfoUrl):
    user_id: str

    normalize_template = "https://wavebox.me/wave/{user_id}/"

    @property
    def primary_names(self) -> list[str]:
        title = self.html.select_one("meta[property='og:title']")["content"]
        match = re.search(r"(.*)のWavebox", title)
        assert match, title
        return list(match.groups())

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []
