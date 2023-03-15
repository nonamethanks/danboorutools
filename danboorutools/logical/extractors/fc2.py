import re

from jinja2 import is_undefined

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class Fc2Url(Url):
    subsite: str
    domain: str
    username: str


class Fc2PostUrl(PostUrl, Fc2Url):
    post_id: int

    normalize_template = "http://{username}.{subsite}.{domain}/blog-entry-{post_id}.html"


class Fc2BlogUrl(ArtistUrl, Fc2Url):
    normalize_template = "http://{username}.{subsite}.{domain}"

    title_selectors = [
        ".site_title a[href*='//{self.username}.']",        # http://mogu08.blog104.fc2.com/
        "#blogTitle",                                       # http://laindell.blog.2nt.com/
        "#branding a[href*='//{self.username}.']",          # http://kudanya.blog42.fc2.com/
    ]

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []

        for selector in self.title_selectors:
            site_title = self.html.select_one(selector.format(self=self))
            if site_title:
                name = site_title.text.strip()
                break
        else:
            raise NotImplementedError(self)

        return [name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []  # too much of a hassle


class Fc2ImageUrl(PostAssetUrl, Fc2Url):
    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


class Fc2PiyoBlogUrl(ArtistUrl, Fc2Url):

    normalize_template = "https://piyo.fc2.com/{username}"


class Fc2PiyoPostUrl(PostUrl, Fc2Url):
    post_id: int

    normalize_template = "https://piyo.fc2.com/{username}/{post_id}"


class Fc2DiaryPostUrl(PostUrl, Fc2Url):
    post_date_string: str

    normalize_template = "http://diary.fc2.com/cgi-sys/ed.cgi/{username}/?{post_date_string}"


class Fc2DiaryArtistUrl(PostUrl, Fc2Url):
    normalize_template = "http://diary.fc2.com/cgi-sys/ed.cgi/{username}"
