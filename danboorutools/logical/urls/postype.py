from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class PostypeUrl(Url):
    ...


class PostypeArtistUrl(ArtistUrl, PostypeUrl):
    username: str

    normalize_template = "https://{username}.postype.com"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one(".ch-home-author-bio .profile-title"))
        return [name_el.text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        assert (bio_el := self.html.select_one(".author-bio"))
        if not bio_el.select("p"):
            return []
        return list(map(Url.parse, extract_urls_from_string(bio_el.select_one("p").text)))


class PostypeSeriesUrl(ArtistAlbumUrl, PostypeUrl):
    series_id: int
    username: str

    normalize_template = "https://{username}.postype.com/series/{series_id}"


class PostypePostUrl(PostUrl, PostypeUrl):
    post_id: int
    username: str

    normalize_template = "https://{username}.postype.com/post/{post_id}"


class PostypeBadArtistUrl(RedirectUrl, PostypeUrl):
    user_id: str

    normalize_template = "https://www.postype.com/profile/{user_id}"


class PostypeImageUrl(PostAssetUrl, PostypeUrl):

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query
