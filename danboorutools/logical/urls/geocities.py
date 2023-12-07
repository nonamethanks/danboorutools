from danboorutools.models.url import ArtistUrl, DeadDomainUrl, PostAssetUrl, PostUrl, Url


class GeocitiesUrl(DeadDomainUrl):
    tld: str
    blog_name: str


class GeocitiesBlogUrl(ArtistUrl, GeocitiesUrl):

    normalize_template = "http://www.geocities.{tld}/{blog_name}/"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.blog_name]

    @property
    def related(self) -> list[Url]:
        return []


class GeocitiesPageUrl(PostUrl, GeocitiesUrl):
    ...


class GeocitiesImageUrl(PostAssetUrl, GeocitiesUrl):
    ...
