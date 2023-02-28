from danboorutools.models.url import ArtistUrl, PostUrl, Url


class InstagramUrl(Url):
    pass


class InstagramPostUrl(PostUrl, InstagramUrl):
    post_id: str

    normalize_string = "https://www.instagram.com/p/{post_id}"


class InstagramArtistUrl(ArtistUrl, InstagramUrl):
    username: str

    normalize_string = "https://www.instagram.com/{username}"
