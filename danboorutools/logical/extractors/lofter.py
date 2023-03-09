from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class LofterUrl(Url):
    pass


class LofterPostUrl(PostUrl, LofterUrl):
    username: str
    post_id: str

    normalize_string = "https://{username}.lofter.com/post/{post_id}"


class LofterArtistUrl(ArtistUrl, LofterUrl):
    username: str

    normalize_string = "https://{username}.lofter.com"

    @property
    def primary_names(self) -> list[str]:
        artist_name = self.html.select_one(".head .title")
        if not artist_name or not artist_name.text:
            raise NotImplementedError(self)
        return [artist_name.text]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        commentary = self.html.select_one(".head .text")
        if not commentary or not commentary.text:
            raise NotImplementedError(self)
        return [Url.parse(u) for u in extract_urls_from_string(commentary.text)]


class LofterImageUrl(PostAssetUrl, LofterUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query
