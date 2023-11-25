from danboorutools.models.url import InfoUrl, Url


class LitlinkUrl(InfoUrl):
    username: str
    normalize_template = "https://lit.link/{username}"

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        name_el = self.html.select_one(".profile-basic-head__name")
        assert name_el, self
        return [name_el.text]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        link_els = self.html.select(".creator-detail-links__col > a")
        if not link_els:
            raise NotImplementedError(self)

        links = [link_el["href"] for link_el in link_els if not link_el["href"].startswith("mailto:")]  # type: ignore[arg-type,union-attr]
        return [Url.parse(link) for link in set(links)]  # type: ignore[arg-type,union-attr]

    @property
    def is_deleted(self) -> bool:
        return "ページが見つかりませんでした" in self.html.text
