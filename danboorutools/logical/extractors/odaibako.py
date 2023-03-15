from danboorutools.models.url import InfoUrl, Url


class OdaibakoUrl(InfoUrl):
    username: str

    normalize_template = "https://odaibako.net/u/{username}"

    @property
    def primary_names(self) -> list[str]:
        artist_box = self.html.select("div.justify-center:not(.adsense_double_rectangle)")
        if len(artist_box) != 1:
            raise NotImplementedError(self)
        return [artist_box[0].select_one("h1").text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return [Url.parse(el["href"]) for el in self.html.select("div.justify-center:not(.adsense_double_rectangle) a")]
