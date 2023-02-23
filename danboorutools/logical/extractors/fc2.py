from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class Fc2Url(Url):
    subsite: str
    domain: str
    username: str


class Fc2PostUrl(PostUrl, Fc2Url):
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"http://{kwargs['username']}.{kwargs['subsite']}.{kwargs['domain']}/blog-entry-{kwargs['post_id']}.html"


class Fc2BlogUrl(ArtistUrl, Fc2Url):

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"http://{kwargs['username']}.{kwargs['subsite']}.{kwargs['domain']}"


class Fc2ImageUrl(PostAssetUrl, Fc2Url):
    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


class Fc2PiyoBlogUrl(ArtistUrl, Fc2Url):

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://piyo.fc2.com/{kwargs['username']}"


class Fc2PiyoPostUrl(PostUrl, Fc2Url):
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://piyo.fc2.com/{kwargs['username']}/{kwargs['post_id']}"


class Fc2DiaryPostUrl(PostUrl, Fc2Url):
    post_date_string: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"http://diary.fc2.com/cgi-sys/ed.cgi/{kwargs['username']}/?{kwargs['post_date_string']}"


class Fc2DiaryArtistUrl(PostUrl, Fc2Url):
    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"http://diary.fc2.com/cgi-sys/ed.cgi/{kwargs['username']}"
