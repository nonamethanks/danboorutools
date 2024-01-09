from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class LivedoorUrl(Url):
    ...


class LivedoorBlogUrl(ArtistUrl, LivedoorUrl):
    username: str
    normalize_template = "http://blog.livedoor.jp/{username}/"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class LivedoorBlogArchiveUrl(PostUrl, LivedoorUrl):
    username: str
    post_id: int
    normalize_template = "http://blog.livedoor.jp/{username}/archives/{post_id}.html"


class LivedoorImageUrl(PostAssetUrl, LivedoorUrl):
    username: str


class LiveDoorAaaArtistUrl(ArtistUrl, LivedoorUrl):
    username: str
    subdomain: str
    is_deleted = True

    normalize_template = "http://{subdomain}.livedoor.jp/~{username}/"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class LiveDoorAaaImageUrl(PostAssetUrl, LivedoorUrl):
    username: str
    subdomain: str
    is_deleted = True
