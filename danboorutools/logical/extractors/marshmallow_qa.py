from danboorutools.models.url import InfoUrl, Url


class MarshmallowQaUrl(InfoUrl):
    username: str

    normalize_template = "https://marshmallow-qa.com/{username}"

    # @property
    # def primary_names(self) -> list[str]:
    #     return self.html.select_one(".card-body h3").text

    # @property
    # def secondary_names(self) -> list[str]:
    #     handle = self.html.select_one(".card-body .small.text-muted")
    #     assert handle.text.startswith("@"), (handle, self)
    #     return handle.text.removeprefix("@")

    # @property
    # def related(self) -> list[Url]:
    #     return [
    #         Url.parse(url.text) for url in
    #         self.html.select(".card-body .list-inline a")
    #     ]

    # protected by cloudflare v2, no point in trying too hard for such a shitty site

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []
