from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class BoothUrl(Url):
    pass


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


class BoothItemListUrl(ArtistAlbumUrl, BoothUrl):

    username: str
    item_list_id: str

    normalize_string = "https://{username}.booth.pm/item_lists/{item_list_id}"


class BoothArtistUrl(ArtistUrl, BoothUrl):
    username: str | None
    user_id: int | None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        if username := kwargs.get("username"):
            return f"https://{username}.booth.pm"
        else:
            raise NotImplementedError


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
        return self.parsed_url.url_without_params.replace("_base_resized", "")
