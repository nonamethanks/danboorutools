import re
from functools import cached_property

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class InprntUrl(Url):
    ...


class InprntArtistUrl(ArtistUrl, InprntUrl):
    username: str

    normalize_template = "https://www.inprnt.com/gallery/{username}"

    @property
    def primary_names(self) -> list[str]:
        # profile_html = self.session.get(f"https://www.inprnt.com/profile/{self.username}").html
        # assert (title_el := profile_html.select_one("meta[property='og:title']"))
        # assert (match := re.match(r"Profile for (.*) - INPRNT", title_el.attrs["content"]))
        # return [match.groups()[0].strip()]
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        # profile_html = self.session.get(f"https://www.inprnt.com/profile/{self.username}").html
        # links = profile_html.select(".container .row .row .col-xs-5 p a[target='_blank']")
        # return parse_list([l.attrs["href"] for l in links], Url)
        return []

    # cloudflare, can't extract shit


class InprntPostUrl(PostUrl, InprntUrl):
    username: str
    post_title: str

    normalize_template = "https://www.inprnt.com/discover/image/{username}/{post_title}"

    @cached_property
    def gallery_url(self) -> str:
        return InprntArtistUrl.build(username=self.username)


class InprntImageUrl(PostAssetUrl, InprntUrl):
    @property
    def full_size(self) -> str:
        return re.sub(r"\/(\w+)\.(\w+)$", r"/\1@2x.\2", self.parsed_url.raw_url)
