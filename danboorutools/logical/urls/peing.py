import re

from danboorutools.models.url import InfoUrl, Url


class PeingUrl(Url):
    ...


class PeingUserUrl(InfoUrl, PeingUrl):
    username: str
    normalize_template = "https://peing.net/{username}"

    @property
    def primary_names(self) -> list[str]:
        assert (title_el := self.html.select_one("meta[property='og:title']"))
        assert (name_match := re.match(r"^You can listen anonymously!(.*)'s Questionbox$", title_el["content"]))
        return list(name_match.groups())

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []
