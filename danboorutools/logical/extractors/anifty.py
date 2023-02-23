from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class AniftyUrl(Url):
    pass


class AniftyPostUrl(PostUrl, AniftyUrl):

    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        return f"https://anifty.jp/creations/{post_id}"


class AniftyArtistUrl(ArtistUrl, AniftyUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        username = kwargs["username"]
        return f"https://anifty.jp/@{username}"


class AniftyArtistImageUrl(GalleryAssetUrl, AniftyUrl):
    artist_hash: str
    filename: str

    @property
    def full_size(self) -> str:
        return f"https://storage.googleapis.com/anifty-media/creation/{self.artist_hash}/{self.filename}"


class AniftyImageUrl(PostAssetUrl, AniftyUrl):
    artist_hash: str
    filename: str

    @property
    def full_size(self) -> str:
        return f"https://storage.googleapis.com/anifty-media/creation/{self.artist_hash}/{self.filename}"


class AniftyTokenUrl(RedirectUrl, AniftyUrl):  # redirects to AniftyPostUrl # TODO: maybe redirecturls should specify where they redirect?
    token_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        token_id = kwargs["token_id"]
        return f"https://anifty.jp/tokens/{token_id}"
