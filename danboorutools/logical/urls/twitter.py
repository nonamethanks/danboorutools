from functools import cached_property

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions.twitter import TwitterSession, TwitterUserData
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class TwitterUrl(Url):
    session = TwitterSession()


class TwitterArtistUrl(ArtistUrl, TwitterUrl):
    username: str

    normalize_template = "https://twitter.com/{username}"

    @property
    def primary_names(self) -> list[str]:
        try:
            return [self.artist_data.name]
        except DeadUrlError:
            return []

    @property
    def secondary_names(self) -> list[str]:
        names = [self.username]
        try:
            return [*names, f"twitter {self.user_id}"]
        except DeadUrlError:
            return names

    @property
    def related(self) -> list[Url]:
        try:
            urls = self.artist_data.related_urls
        except DeadUrlError:
            urls = []

        from danboorutools.logical.urls.skeb import SkebArtistUrl

        skeb = SkebArtistUrl.build(username=self.username)
        if not skeb.is_deleted:
            urls += [skeb]

        try:
            intent_url = TwitterIntentUrl.build(intent_id=self.artist_data.id)
        except DeadUrlError:
            pass
        else:
            intent_url.artist_data = self.artist_data
            urls += [intent_url]

        return list(dict.fromkeys(urls))

    @property
    def user_id(self) -> int:
        return self.artist_data.id

    @property
    def artist_data(self) -> TwitterUserData:
        return self.session.user_data(user_name=self.username)

    def subscribe(self) -> None:
        return self.session.subscribe(self.username)


class TwitterPostUrl(PostUrl, TwitterUrl):
    post_id: int
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://twitter.com/{kwargs["username"]}/status/{kwargs["post_id"]}"

    @property
    def gallery(self) -> TwitterArtistUrl:
        return TwitterArtistUrl.build(username=self.username)


class TwitterIntentUrl(InfoUrl, TwitterUrl):
    intent_id: int

    normalize_template = "https://twitter.com/intent/user?user_id={intent_id}"

    @property
    def user_url(self) -> TwitterArtistUrl:
        return TwitterArtistUrl.build(username=self.artist_data.screen_name)

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        return [self.user_url]

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        return self.user_url.primary_names

    @property
    def secondary_names(self) -> list[str]:
        if self.is_deleted:
            return [f"twitter {self.intent_id}"]
        return self.user_url.secondary_names

    @cached_property
    def artist_data(self) -> TwitterUserData:
        return self.session.user_data(user_id=self.intent_id)


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

    normalize_template = "https://twitter.com/i/status/{post_id}"


class TwitterArtistImageUrl(GalleryAssetUrl, TwitterUrl):
    user_id: int
    file_path: str

    @property
    def full_size(self) -> str:
        return f"https://{self.parsed_url.hostname}/{self.file_path}"


class TwitterShortenerUrl(RedirectUrl, TwitterUrl):
    shortener_id: str

    normalize_template = "https://t.co/{shortener_id}"
