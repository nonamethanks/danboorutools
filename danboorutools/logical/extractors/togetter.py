from functools import cached_property

from danboorutools.logical.extractors.twitter import TwitterArtistUrl
from danboorutools.models.url import ArtistUrl, PostUrl, Url


class TogetterUrl(Url):
    @cached_property
    def is_deleted(self) -> bool:
        response = self.session.get(self.normalized_url)
        if response.url.strip("/") == "https://min.togetter.com":
            return True
        elif response.url == self.normalized_url:
            return False
        else:
            raise NotImplementedError(self, response.url)


class TogetterArtistUrl(ArtistUrl, TogetterUrl):
    username: str

    normalize_template = "https://min.togetter.com/id/{username}"

    @property
    def related(self) -> list[Url]:
        return [Url.build(TwitterArtistUrl, username=self.username)]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def primary_names(self) -> list[str]:
        return []


class TogetterPostUrl(PostUrl, TogetterUrl):
    post_id: str

    normalize_template = "https://min.togetter.com/{post_id}"

    @property
    def gallery(self) -> TogetterArtistUrl:
        url = Url.parse(self.html.select_one(".info_box .authour_link")["href"])
        if not isinstance(url, TogetterArtistUrl):
            raise NotImplementedError(self, url)
        return url


class TogetterLiUrl(PostUrl, TogetterUrl):
    li_id: int

    normalize_template = "https://togetter.com/li/{li_id}"
