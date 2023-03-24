from danboorutools.models.url import InfoUrl, Url


class ProfcardUrl(InfoUrl):
    user_id: str

    normalize_template = "https://profcard.info/u/{user_id}"

    @property
    def primary_names(self) -> list[str]:
        return [self.html.select_one(".userName").text]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return [Url.parse(u["href"]) for u in self.html.select(".card a")]
