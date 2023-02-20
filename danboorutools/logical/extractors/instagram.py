from danboorutools.models.url import ArtistUrl, PostUrl, Url


class InstagramUrl(Url):
    pass


class InstagramPostUrl(PostUrl, InstagramUrl):
    post_id: str


class InstagramArtistUrl(ArtistUrl, InstagramUrl):
    username: str
