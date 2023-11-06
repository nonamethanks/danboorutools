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
        page_title = self.html.select_one("title").text
        pattern = rf"^(.*)（@{self.username}） - カクヨム$"
        assert (match := re.match(pattern, page_title)), page_title
        name, = match.groups()
        return [name.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        twitter_url = self.html.select_one("[class^='UserHeaderItem_twitterLink__'] a")["href"]
        parsed_url = Url.parse(twitter_url)
        assert isinstance(parsed_url, TwitterArtistUrl)
        return [Url.parse(twitter_url)]


class KakuyomuPostUrl(PostUrl, KakuyomuUrl):
    post_id: int

    normalize_template = "https://kakuyomu.jp/works/{post_id}"


    @property
    def gallery(self) -> KakuyomuArtistUrl:
        user_url = Url.parse(urljoin("https://kakuyomu.jp", self.html.select_one("#workAuthor-activityName a")["href"]))
        assert isinstance(user_url, KakuyomuArtistUrl), user_url
        return user_url
