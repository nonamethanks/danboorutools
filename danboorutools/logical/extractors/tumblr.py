import re

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class TumblrUrl(Url):
    pass


class TumblrPostUrl(PostUrl, TumblrUrl):
    post_id: int
    blog_name: str

    normalize_string = "https://{blog_name}.tumblr.com/post/{post_id}"


class TumblrPostRedirectUrl(RedirectUrl, TumblrUrl):
    blog_name: str
    redirect_id: str
    title: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if title := kwargs.get("title"):
            return f"https://at.tumblr.com/{kwargs['blog_name']}/{title}/{kwargs['redirect_id']}"
        else:
            return f"https://at.tumblr.com/{kwargs['blog_name']}/{kwargs['redirect_id']}"


class TumblrArtistUrl(ArtistUrl, TumblrUrl):
    blog_name: str

    normalize_string = "https://{blog_name}.tumblr.com"


class TumblrImageUrl(PostAssetUrl, TumblrUrl):
    @property
    def full_size(self) -> str:
        if re.search(r"\/s\d+x\d+\/", self.parsed_url.raw_url):
            return re.sub(r"\/s\d+x\d+\/", "/s21000x21000/", self.parsed_url.raw_url)
        else:
            raise NotImplementedError
