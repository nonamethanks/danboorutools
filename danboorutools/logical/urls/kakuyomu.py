import re
from urllib.parse import urljoin

from danboorutools.logical.urls.twitter import TwitterArtistUrl
from danboorutools.models.url import ArtistUrl, PostUrl, Url


class KakuyomuUrl(Url):
    pass


class KakuyomuArtistUrl(ArtistUrl, KakuyomuUrl):
    username: str

    normalize_template = "https://kakuyomu.jp/users/{username}"

    @property
    def primary_names(self) -> list[str]:
        assert (page_el := self.html.select_one("title"))
        page_title = page_el.text
        pattern = rf"^(.*)（@{self.username}） - カクヨム$"
        assert (match := re.match(pattern, page_title)), page_title
        name, = match.groups()
        return [name.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        assert (twitter_el := self.html.select_one("[class^='UserHeaderItem_twitterLink__'] a"))
        assert isinstance(twitter_url := twitter_el["href"], str)
        parsed_url = Url.parse(twitter_url)
        assert isinstance(parsed_url, TwitterArtistUrl)
        return [Url.parse(twitter_url)]


class KakuyomuPostUrl(PostUrl, KakuyomuUrl):
    post_id: int

    normalize_template = "https://kakuyomu.jp/works/{post_id}"

    @property
    def gallery(self) -> KakuyomuArtistUrl:
        selector = ".NewBox_box__45ont  .partialGiftWidgetActivityName a[href^='/users/'].LinkAppearance_link__POVTP"
        assert (gallery_el := self.html.select_one(selector))
        assert isinstance(gallery_url := gallery_el["href"], str)
        user_url = Url.parse(urljoin("https://kakuyomu.jp", gallery_url))
        assert isinstance(user_url, KakuyomuArtistUrl), user_url
        return user_url
