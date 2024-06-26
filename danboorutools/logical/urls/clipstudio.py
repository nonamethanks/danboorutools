from __future__ import annotations

from danboorutools.models.url import ArtistUrl, DeadDomainUrl, InfoUrl, PostUrl, Url


class ClipStudioUrl(Url):
    pass


class ClipStudioUserSearchUrl(ArtistUrl, ClipStudioUrl):
    username: str
    normalize_template = "https://assets.clip-studio.com/en-us/search?user={username}"

    # @property  # doesn't work because clip-studio uses jRender to render stuff. I'd have to use selenium but it's not worth it
    # def profile_url(self) -> ClipStudioProfileUrl:
    #     post = Url.parse(self.html.select_one("a.materialCard__cardContentBlock")["href"])
    #     if not isinstance(post, ClipStudioAssetPostUrl):
    #         raise NotImplementedError(post, self)

    #     return post.profile

    @property
    def primary_names(self) -> list[str]:
        return [self.username]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []


class ClipStudioAssetPostUrl(PostUrl, ClipStudioUrl):
    asset_id: int
    normalize_template = "https://assets.clip-studio.com/en-us/detail?id={asset_id}"

    @property
    def profile(self) -> ClipStudioProfileUrl:
        profile_url = ClipStudioProfileUrl.parse_and_assert(self.html.select_one(".author__moreDetail > a")["href"])
        return profile_url


class ClipStudioProfileUrl(InfoUrl, ClipStudioUrl):
    profile_id: str
    normalize_template = "https://profile.clip-studio.com/en-us/profile/{profile_id}"

    @property
    def primary_names(self) -> list[str]:
        return [self.html.select_one(".userProfile__name").text]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        urls = self.html.select(".userProfile__links a.userProfile__socialButton")

        return [Url.parse(u["href"]) for u in urls]


class ClipStudioBlogUrl(DeadDomainUrl, InfoUrl, ClipStudioUrl):
    blog_name: str

    normalize_template = "http://{blog_name}.sees.clip-studio.com/site/"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.blog_name]

    @property
    def related(self) -> list[Url]:
        return []
