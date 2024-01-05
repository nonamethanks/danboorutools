from danboorutools.models.url import ArtistUrl, PostUrl, Url


class SbloUrl(Url):
    ...


class SbloBlogUrl(ArtistUrl, SbloUrl):
    blog_name: str

    normalize_template = "http://{blog_name}.sblo.jp/"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.blog_name]

    @property
    def related(self) -> list[Url]:
        return []


class SbloArticleUrl(PostUrl, SbloUrl):
    blog_name: str
    article_id: int

    normalize_template = "http://{blog_name}.sblo.jp/article/{article_id}.html"
