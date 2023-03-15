import re

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

    @property
    def primary_names(self) -> list[str]:
        title_selectors = [
            f".site_title a[href*='//{self.username}.']",  # http://mogu08.blog104.fc2.com/
            f"#header > h1 > a[href*='//{self.username}.']",  # http://neostargate2013.blog.fc2.com/
        ]
        for selector in title_selectors:
            site_title = self.html.select_one(selector)
            if site_title:
                break
        else:
            raise NotImplementedError(self)

        name = site_title.text.strip()
        if match := re.match(r"^(.*)\(.*\sblog\)$", name):
            name = match.groups()[0]
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
