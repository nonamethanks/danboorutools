from danboorutools.models.url import InfoUrl, Url


class LinktreeUrl(InfoUrl):
    username: str

    normalize_template = "https://linktr.ee/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        url_els = self.html.select("a[data-testid='LinkButton']")
        if not url_els:
            raise NotImplementedError(self)

        return [Url.parse(el.attrs["href"]) for el in url_els]
