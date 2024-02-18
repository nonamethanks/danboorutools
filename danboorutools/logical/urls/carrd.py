from danboorutools.models.url import InfoUrl, Url


class CarrdUrl(InfoUrl):
    username: str

    normalize_template = "https://{username}.carrd.co"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []
