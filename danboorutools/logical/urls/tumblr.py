import re

from danboorutools.logical.sessions.tumblr import TumblrBlogData, TumblrSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class TumblrUrl(Url):
    session = TumblrSession()


class TumblrPostUrl(PostUrl, TumblrUrl):
    post_id: int
    blog_name: str

    normalize_template = "https://{blog_name}.tumblr.com/post/{post_id}"


class TumblrArtistUrl(ArtistUrl, TumblrUrl):
    blog_name: str

    normalize_template = "https://{blog_name}.tumblr.com"

    @property
    def artist_data(self) -> TumblrBlogData:
        return self.session.blog_data(self.blog_name)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.title]

    @property
    def secondary_names(self) -> list[str]:
        return [self.blog_name]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls


class TumblrImageUrl(PostAssetUrl, TumblrUrl):
    dimensions_pattern = re.compile(r"s\d+x\d+(?:_c\d)?")

    @property
    def full_size(self) -> str:
        if self.dimensions_pattern.search(self.parsed_url.raw_url):
            return re.sub(rf"\/{self.dimensions_pattern.pattern}\/", "/s21000x21000/", self.parsed_url.raw_url)
        else:
            raise NotImplementedError
