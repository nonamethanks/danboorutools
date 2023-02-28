from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class Fc2Url(Url):
    subsite: str
    domain: str
    username: str


class Fc2PostUrl(PostUrl, Fc2Url):
    post_id: int

    normalize_string = "http://{username}.{subsite}.{domain}/blog-entry-{post_id}.html"


class Fc2BlogUrl(ArtistUrl, Fc2Url):

    normalize_string = "http://{username}.{subsite}.{domain}"


class Fc2ImageUrl(PostAssetUrl, Fc2Url):
    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


class Fc2PiyoBlogUrl(ArtistUrl, Fc2Url):

    normalize_string = "https://piyo.fc2.com/{username}"


class Fc2PiyoPostUrl(PostUrl, Fc2Url):
    post_id: int

    normalize_string = "https://piyo.fc2.com/{username}/{post_id}"


class Fc2DiaryPostUrl(PostUrl, Fc2Url):
    post_date_string: str

    normalize_string = "http://diary.fc2.com/cgi-sys/ed.cgi/{username}/?{post_date_string}"


class Fc2DiaryArtistUrl(PostUrl, Fc2Url):
    normalize_string = "http://diary.fc2.com/cgi-sys/ed.cgi/{username}"
