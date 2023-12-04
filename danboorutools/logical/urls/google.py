from danboorutools.models.url import ArtistUrl, DeadDomainUrl, InfoUrl, Url


class GoogleUrl(Url):
    ...


class GooglePicasaArtistUrl(DeadDomainUrl, ArtistUrl, GoogleUrl):
    username: str

    normalize_template = "https://picasaweb.google.com/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        if self.username.isnumeric():
            return []
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class GooglePicasaPostUrl(DeadDomainUrl, ArtistUrl, GoogleUrl):
    photo_id: str

    normalize_template = "https://picasaweb.google.com/lh/photo/{photo_id}"


class GoogleProfilesUrl(DeadDomainUrl, InfoUrl, GoogleUrl):
    username: str

    normalize_template = "https://profiles.google.com/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        if self.username.isnumeric():
            return []
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class GooglePlayDeveloperUrl(InfoUrl, GoogleUrl):
    developer_name: str | None = None
    developer_id: int | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        if developer_id := kwargs.get("developer_id"):
            return f"https://play.google.com/store/apps/dev?id={developer_id}"
        elif developer_name := kwargs.get("developer_name"):
            return f"https://play.google.com/store/apps/developer?id={developer_name}"
        else:
            raise NotImplementedError(kwargs)

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        if self.developer_name:
            return [self.developer_name]
        return []

    @property
    def related(self) -> list[Url]:
        return []
