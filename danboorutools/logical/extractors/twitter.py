from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class TwitterUrl(Url):
    pass


class TwitterPostUrl(PostUrl, TwitterUrl):
    post_id: int
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://twitter.com/{kwargs['username']}/status/{kwargs['post_id']}"


class TwitterArtistUrl(ArtistUrl, TwitterUrl):
    username: str

    normalize_string = "https://twitter.com/{username}"


class TwitterAssetUrl(PostAssetUrl, TwitterUrl):
    file_path: str

    @property
    def full_size(self) -> str:
        if self.parsed_url.extension != "mp4":
            return f"https://{self.parsed_url.hostname}/{self.file_path}:orig"
        else:
            raise NotImplementedError


class TwitterOnlyStatusUrl(RedirectUrl, TwitterUrl):
    post_id: int

    normalize_string = "https://twitter.com/i/status/{post_id}"


class TwitterIntentUrl(RedirectUrl, TwitterUrl):
    intent_id: int

    normalize_string = "https://twitter.com/intent/user?user_id={intent_id}"


class TwitterArtistImageUrl(GalleryAssetUrl, TwitterUrl):
    user_id: int
    file_path: str

    @property
    def full_size(self) -> str:
        return f"https://{self.parsed_url.hostname}/{self.file_path}"


class TwitterShortenerUrl(RedirectUrl, TwitterUrl):
    shortener_id: str

    normalize_string = "https://t.co/{shortener_id}"
