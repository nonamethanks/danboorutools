from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class AniftyUrl(Url):
    pass


class AniftyPostUrl(PostUrl, AniftyUrl):
    normalization = "https://anifty.jp/creations/{post_id}"

    post_id: int


class AniftyArtistUrl(ArtistUrl, AniftyUrl):
    normalization = "https://anifty.jp/@{username}"

    username: str


class AniftyArtistImageUrl(GalleryAssetUrl, AniftyUrl):
    artist_hash: str
    image_type: str


class AniftyImageUrl(PostAssetUrl, AniftyUrl):
    artist_hash: str


class AniftyTokenUrl(RedirectUrl, AniftyUrl):  # redirects to AniftyPostUrl # TODO: maybe redirecturls should specify where they redirect?
    token_id: int
