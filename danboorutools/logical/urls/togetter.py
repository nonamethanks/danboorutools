from functools import cached_property

from danboorutools.logical.urls.twitter import TwitterArtistUrl
from danboorutools.models.url import ArtistUrl, PostUrl, Url


class TogetterUrl(Url):
    pass


class TogetterArtistUrl(ArtistUrl, TogetterUrl):
    username: str

    normalize_template = "https://min.togetter.com/id/{username}"

    @property
    def related(self) -> list[Url]:
        return [TwitterArtistUrl.build(username=self.username)]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def primary_names(self) -> list[str]:
        return []

    @cached_property
    def is_deleted(self) -> bool:
        return self.session.get(self.normalized_url).url == "https://min.togetter.com/"


class TogetterPostUrl(PostUrl, TogetterUrl):
    post_id: str

    normalize_template = "https://min.togetter.com/{post_id}"

    @cached_property
    def gallery(self) -> TogetterArtistUrl:
        gallery_link_el = self.html.select_one(".info_box .authour_link")
        assert gallery_link_el
        url = TogetterArtistUrl.parse_and_assert(gallery_link_el["href"])
        return url


class TogetterLiUrl(PostUrl, TogetterUrl):
    li_id: int

    normalize_template = "https://togetter.com/li/{li_id}"
