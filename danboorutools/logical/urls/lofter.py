from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class LofterUrl(Url):
    pass


class LofterPostUrl(PostUrl, LofterUrl):
    username: str
    post_id: str

    normalize_template = "https://{username}.lofter.com/post/{post_id}"


class LofterArtistUrl(ArtistUrl, LofterUrl):
    username: str

    normalize_template = "https://{username}.lofter.com"

    _commentary_css = (
        ".head .text",  # https://lbgu1.lofter.com/
        ".selfinfo .text",  # https://jiaojiaojiazuzy.lofter.com/
        ".p-homepage #j-about",  # https://chaodazu.lofter.com/
    )

    @property
    def primary_names(self) -> list[str]:
        assert (artist_name := self.html.select_one("title"))
        return [artist_name.text]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        commentary = None
        for selector in self._commentary_css:
            commentary = self.html.select_one(selector)
            if commentary:
                break
        if not commentary or not commentary.text:
            raise NotImplementedError(self)
        return [Url.parse(u) for u in extract_urls_from_string(commentary.text)]


class LofterImageUrl(PostAssetUrl, LofterUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query


class LofterRedirectArtistUrl(RedirectUrl, LofterUrl):
    blog_id: int
    normalize_template = "https://www.lofter.com/mentionredirect.do?blogId={blog_id}"
