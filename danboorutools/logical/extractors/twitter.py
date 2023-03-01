from danboorutools.exceptions import UrlIsDeleted
from danboorutools.logical.sessions.twitter import TwitterSession  # pylint: disable=E0401,E0611 # False positive
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import settable_property


class TwitterUrl(Url):
    session = TwitterSession()


class TwitterPostUrl(PostUrl, TwitterUrl):
    post_id: int
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://twitter.com/{kwargs['username']}/status/{kwargs['post_id']}"


class TwitterArtistUrl(ArtistUrl, TwitterUrl):
    username: str

    normalize_string = "https://twitter.com/{username}"

    @property
    def primary_names(self) -> list[str]:
        return [self._artist_data["name"]]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username, f"twitter {self.user_id}"]

    @property
    def related(self) -> list[Url]:
        # pylint: disable=import-outside-toplevel
        from danboorutools.logical.extractors.skeb import SkebArtistUrl

        related: list[Url] = []
        related += [Url.build(TwitterIntentUrl, intent_id=self.user_id)]

        for field in ["url", "description"]:
            try:
                related += [Url.parse(url["expanded_url"])
                            for url in self._artist_data["entities"][field]["urls"]
                            if not url["expanded_url"].endswith("...")]
            except KeyError:
                pass
        skeb = Url.build(SkebArtistUrl, username=self.username)
        if not skeb.is_deleted:
            related += [skeb]

        return related

    @property
    def user_id(self) -> int:
        return self._artist_data["id"]

    @property
    def _artist_data(self) -> dict:
        return self.session.user_data(username=self.username)

    @settable_property
    def is_deleted(self) -> bool:
        try:
            self._artist_data
        except UrlIsDeleted:
            return True
        else:
            return False


class TwitterIntentUrl(InfoUrl, TwitterUrl):
    intent_id: int

    normalize_string = "https://twitter.com/intent/user?user_id={intent_id}"

    @property
    def related(self) -> list[Url]:
        return [self.build(TwitterArtistUrl, username=self._artist_data["screen_name"])]

    @property
    def _artist_data(self) -> dict:
        return self.session.user_data(user_id=self.intent_id)

    @settable_property
    def is_deleted(self) -> bool:
        try:
            self._artist_data
        except UrlIsDeleted:
            return True
        else:
            return False


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


class TwitterArtistImageUrl(GalleryAssetUrl, TwitterUrl):
    user_id: int
    file_path: str

    @property
    def full_size(self) -> str:
        return f"https://{self.parsed_url.hostname}/{self.file_path}"


class TwitterShortenerUrl(RedirectUrl, TwitterUrl):
    shortener_id: str

    normalize_string = "https://t.co/{shortener_id}"
