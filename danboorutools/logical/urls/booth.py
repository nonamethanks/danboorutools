from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class BoothUrl(Url):
    pass


class BoothItemListUrl(ArtistAlbumUrl, BoothUrl):

    username: str
    item_list_id: str

    normalize_template = "https://{username}.booth.pm/item_lists/{item_list_id}"


class BoothArtistUrl(ArtistUrl, BoothUrl):
    username: str | None
    user_id: int | None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        if username := kwargs.get("username"):
            return f"https://{username}.booth.pm"
        else:
            raise NotImplementedError

    @property
    def primary_names(self) -> list[str]:
        if self.private:
            return []
        name_el = self.html.select_one(".home-link-container__nickname a") or self.html.select_one(".shop-name-label.display_title")
        return [name_el.text]

    @property
    def secondary_names(self) -> list[str]:
        if self.username:
            return [self.username]
        else:
            raise NotImplementedError(self)

    @property
    def related(self) -> list[Url]:
        if self.private:
            return []
        if not (url_els := self.html.select(".shop-contacts__link a, a:has(> .shop__text--link)")):
            raise NotImplementedError(self)
        return [Url.parse(el["href"]) for el in url_els if el["href"].startswith("http")]

    @property
    def private(self) -> bool:
        return "Currently, this shop is private" in str(self.html)


class BoothItemUrl(PostUrl, BoothUrl):
    username: str | None
    item_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        item_id: int = kwargs["item_id"]
        if username := kwargs.get("username"):
            return f"https://{username}.booth.pm/items/{item_id}"
        else:
            return f"https://booth.pm/items/{item_id}"

    @property
    def gallery(self) -> BoothArtistUrl:
        if self.username:
            return BoothArtistUrl.build(username=self.username)

        raise NotImplementedError(self)


class BoothImageUrl(PostAssetUrl, BoothUrl):
    item_id: int

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url.replace("_base_resized", "")


class BoothProfileImageUrl(PostAssetUrl, BoothUrl):
    user_id: int | None
    # user_uuid: str | None

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query.replace("_base_resized", "")
