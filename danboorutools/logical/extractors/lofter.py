from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class LofterUrl(Url):
    pass


class LofterPostUrl(PostUrl, LofterUrl):
    username: str
    post_id: str

    normalize_string = "https://{username}.lofter.com/post/{post_id}"


class LofterArtistUrl(ArtistUrl, LofterUrl):
    username: str

    normalize_string = "https://{username}.lofter.com"


class LofterImageUrl(PostAssetUrl, LofterUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query
