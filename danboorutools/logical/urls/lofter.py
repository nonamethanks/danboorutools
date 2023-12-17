from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class LofterUrl(Url):
    pass


class LofterArtistUrl(ArtistUrl, LofterUrl):
    username: str

    normalize_template = "https://{username}.lofter.com"

    @property
    def primary_names(self) -> list[str]:
        assert (artist_name := self.html.select_one("title"))
        return [artist_name.text]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        assert (commentary_el := self.html.select_one("meta[name='Description']"))
        return [Url.parse(u) for u in extract_urls_from_string(commentary_el["content"])]


class LofterPostUrl(PostUrl, LofterUrl):
    username: str
    post_id: str

    normalize_template = "https://{username}.lofter.com/post/{post_id}"

    @property
    def gallery(self) -> LofterArtistUrl:
        return LofterArtistUrl.build(username=self.username)


class LofterImageUrl(PostAssetUrl, LofterUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query


class LofterRedirectArtistUrl(RedirectUrl, LofterUrl):
    blog_id: int
    normalize_template = "https://www.lofter.com/mentionredirect.do?blogId={blog_id}"
