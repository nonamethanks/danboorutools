from danboorutools.logical.sessions.plurk import PlurkArtistData, PlurkSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PlurkUrl(Url):
    session = PlurkSession()


class PlurkPostUrl(PostUrl, PlurkUrl):
    post_id: str

    normalize_template = "https://www.plurk.com/p/{post_id}"


class PlurkArtistUrl(ArtistUrl, PlurkUrl):
    username: str

    normalize_template = "https://www.plurk.com/{username}"

    @property
    def artist_data(self) -> PlurkArtistData:
        return self.session.user_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        if self.artist_data.display_name != self.artist_data.full_name:
            raise NotImplementedError(self, self.artist_data.display_name, self.artist_data.full_name)
        return [self.artist_data.display_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls


class PlurkImageUrl(PostAssetUrl, PlurkUrl):
    image_id: str

    @property
    def full_size(self) -> str:
        return f"https://images.plurk.com/{self.image_id}.{self.parsed_url.extension}"
