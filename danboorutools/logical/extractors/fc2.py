from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class Fc2Url(Url):
    subsite: str
    username: str


class Fc2PostUrl(PostUrl, Fc2Url):
    post_id: int


class Fc2BlogUrl(ArtistUrl, Fc2Url):
    ...


class Fc2ImageUrl(PostAssetUrl, Fc2Url):
    ...


class Fc2PiyoBlogUrl(ArtistUrl, Fc2Url):
    username: str


class Fc2PiyoPostUrl(PostUrl, Fc2Url):
    post_id: int
