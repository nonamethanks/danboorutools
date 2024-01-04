from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class YfrogUrl(Url):
    is_deleted = True


class YfrogArtistUrl(ArtistUrl, YfrogUrl):
    username: str

    normalize_template = "http://yfrog.com/user/{username}/photos"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class YfrogPostUrl(PostUrl, YfrogUrl):
    post_id: str

    normalize_template = "http://yfrog.com/{post_id}"


class YfrogImageUrl(PostAssetUrl, YfrogUrl):
    ...
