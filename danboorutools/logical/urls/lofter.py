from functools import cached_property

from danboorutools.logical.sessions.lofter import LofterBlogData, LofterSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url, parse_list
from danboorutools.util.misc import extract_urls_from_string


class LofterUrl(Url):
    session = LofterSession()


class LofterArtistUrl(ArtistUrl, LofterUrl):
    username: str

    normalize_template = "https://{username}.lofter.com"

    @property
    def artist_data(self) -> LofterBlogData:
        return self.session.blog_data(blog_name=self.username)

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        return [self.artist_data.blogNickName]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        return parse_list(extract_urls_from_string(self.artist_data.selfIntro), ArtistUrl)


class LofterPostUrl(PostUrl, LofterUrl):
    username: str
    post_id: str

    normalize_template = "https://{username}.lofter.com/post/{post_id}"

    @cached_property
    def gallery(self) -> LofterArtistUrl:
        return LofterArtistUrl.build(username=self.username)


class LofterImageUrl(PostAssetUrl, LofterUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query


class LofterRedirectArtistUrl(RedirectUrl, LofterUrl):
    blog_id: int
    normalize_template = "https://www.lofter.com/mentionredirect.do?blogId={blog_id}"
