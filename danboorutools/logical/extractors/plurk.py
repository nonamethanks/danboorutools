from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PlurkUrl(Url):
    pass


class PlurkPostUrl(PostUrl, PlurkUrl):
    post_id: str

    normalize_string = "https://www.plurk.com/p/{post_id}"


class PlurkArtistUrl(ArtistUrl, PlurkUrl):
    username: str

    normalize_string = "https://www.plurk.com/{username}"


class PlurkImageUrl(PostAssetUrl, PlurkUrl):
    image_id: str

    @property
    def full_size(self) -> str:
        return f"https://images.plurk.com/{self.image_id}.{self.parsed_url.extension}"
