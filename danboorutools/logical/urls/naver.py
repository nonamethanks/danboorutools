from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class NaverUrl(Url):
    pass


class NaverCafeArtistUrl(ArtistUrl, NaverUrl):
    username: str


class NaverCafePostUrl(PostUrl, NaverUrl):
    username: str
    post_id: int

    normalize_template = "http://cafe.naver.com/{username}/{post_id}"


class NaverBlogArtistUrl(ArtistUrl, NaverUrl):
    username: str

    normalize_template = "http://blog.naver.com/{username}"


class NaverBlogPostUrl(ArtistUrl, NaverUrl):
    username: str
    post_id: int

# class NaverImageUrl(PostAssetUrl, NaverUrl):
#     ...
