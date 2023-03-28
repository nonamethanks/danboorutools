from danboorutools.logical.urls.twitter import TwitterArtistUrl
from danboorutools.models.url import InfoUrl, Url


class TwpfUrl(InfoUrl):
    username: str
    normalize_template = "https://twpf.jp/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        twitter_url = TwitterArtistUrl.build(username=self.username)
        return [twitter_url]
