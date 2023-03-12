from danboorutools.models.url import InfoUrl, Url


class LitlinkUrl(InfoUrl):
    username: str
    normalize_string = "https://lit.link/{username}"

    @property
    def primary_names(self) -> list[str]:
        return [self.html.select_one(".profile-basic-head__name").text]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        links = self.html.select(".creator-detail-links__col > a")
        if not links:
            raise NotImplementedError(self)

        return [Url.parse(el["href"]) for el in links]
