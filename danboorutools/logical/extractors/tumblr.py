from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class TumblrUrl(Url):
    pass


class TumblrPostUrl(PostUrl, TumblrUrl):
    post_id: int
    blog_name: str


class TumblrPostRedirectUrl(RedirectUrl, TumblrUrl):
    blog_name: str
    redirect_id: str


class TumblrArtistUrl(ArtistUrl, TumblrUrl):
    blog_name: str


class TumblrImageUrl(PostAssetUrl, TumblrUrl):
    ...
