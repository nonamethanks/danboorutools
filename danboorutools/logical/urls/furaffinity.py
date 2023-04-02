from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class FuraffinityUrl(Url):
    pass


class FuraffinityPostUrl(PostUrl, FuraffinityUrl):
    post_id: int

    normalize_template = "https://www.furaffinity.net/view/{post_id}"


class FuraffinityArtistUrl(ArtistUrl, FuraffinityUrl):
    username: str

    normalize_template = "https://www.furaffinity.net/user/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return [Url.parse(el["href"]) for el in self.html.select(".user-contact-user-info a")]


class FuraffinityImageUrl(PostAssetUrl, FuraffinityUrl):
    username: str | None
    post_id: int | None

    @property
    def full_size(self) -> str:
        if self.parsed_url.subdomain == "d":
            return self.parsed_url.raw_url
        else:
            raise NotImplementedError


class FuraffinityArtistImageUrl(GalleryAssetUrl, FuraffinityUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url
