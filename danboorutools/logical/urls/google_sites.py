

from functools import cached_property

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class GoogleSitesUrl(Url):
    ...


class GoogleSitesArtistUrl(ArtistUrl, GoogleSitesUrl):
    site_name: str

    normalize_template = "https://sites.google.com/site/{site_name}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        if self.site_name.isnumeric():
            return []
        return [self.site_name]

    @property
    def related(self) -> list[Url]:
        return []


class GoogleSitesPostUrl(PostUrl, GoogleSitesUrl):
    site_name: str
    post_path: str

    normalize_template = "https://sites.google.com/site/{site_name}/_/rsrc/{post_path}"

    @cached_property
    def gallery(self) -> GoogleSitesArtistUrl:
        return GoogleSitesArtistUrl.build(site_name=self.site_name)


class GoogleSitesImageUrl(PostAssetUrl, GoogleSitesUrl):
    site_name: str
