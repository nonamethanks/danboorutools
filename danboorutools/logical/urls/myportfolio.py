from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.models.url import InfoUrl, PostAssetUrl, Url


class MyportfolioUrl(Url):
    ...


class MyportfolioArtistUrl(InfoUrl, MyportfolioUrl):
    username: str

    normalize_template = "https://{username}.myportfolio.com"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []

    @property
    def is_deleted(self) -> bool:
        return ParsableUrl(self.session.get(self.normalized_url).url).domain == "adobe.com"


class MyportfolioImageUrl(PostAssetUrl, MyportfolioUrl):
    ...
