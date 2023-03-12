from danboorutools.models.url import ArtistUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class BcyUrl(Url):
    pass


class BcyArtistUrl(ArtistUrl, BcyUrl):
    user_id: int

    normalize_string = "https://bcy.net/u/{user_id}"

    @property
    def primary_names(self) -> list[str]:
        return [self.html.select_one(".user-info .user-info-name").text]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        description = self.html.select_one(".user-info .user-info-self-intro").text
        return [Url.parse(u) for u in extract_urls_from_string(description)]


class BcyPostUrl(PostUrl, BcyUrl):
    post_id: int

    normalize_string = "https://bcy.net/item/detail/{post_id}"


class OldBcyPostUrl(PostUrl, BcyUrl):
    first_id: int
    second_id: int

    normalize_string = "http://bcy.net/illust/detail/{first_id}/{second_id}"

    is_deleted = True
