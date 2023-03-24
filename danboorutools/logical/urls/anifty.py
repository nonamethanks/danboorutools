from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class AniftyUrl(Url):
    pass


class AniftyPostUrl(PostUrl, AniftyUrl):

    post_id: int

    normalize_template = "https://anifty.jp/creations/{post_id}"


class AniftyArtistUrl(ArtistUrl, AniftyUrl):
    username: str

    normalize_template = "https://anifty.jp/@{username}"


class AniftyArtistImageUrl(GalleryAssetUrl, AniftyUrl):
    artist_hash: str
    filename: str

    @property
    def full_size(self) -> str:
        return "https://storage.googleapis.com/anifty-media/creation/{self.artist_hash}/{self.filename}"


class AniftyImageUrl(PostAssetUrl, AniftyUrl):
    artist_hash: str
    filename: str

    @property
    def full_size(self) -> str:
        return "https://storage.googleapis.com/anifty-media/creation/{self.artist_hash}/{self.filename}"


class AniftyTokenUrl(RedirectUrl, AniftyUrl):  # redirects to AniftyPostUrl # TODO: maybe redirecturls should specify where they redirect?
    token_id: int

    normalize_template = "https://anifty.jp/tokens/{token_id}"
