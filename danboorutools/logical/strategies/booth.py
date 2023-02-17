from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class BoothUrl(Url):
    pass


class BoothItemUrl(PostUrl, BoothUrl):
    normalization = "https://booth.pm/en/items/{item_id}"

    username: str | None
    item_id: int

    @classmethod
    def _normalize_from_properties(cls, **kwargs) -> str:
        username: str | None = kwargs.get("username")
        item_id: int = kwargs["item_id"]
        if username:
            return f"https://{username}.booth.pm/en/items/{item_id}"
        else:
            return f"https://booth.pm/en/items/{item_id}"


class BoothItemListUrl(ArtistAlbumUrl, BoothUrl):
    normalization = "https://{username}.booth.pm/en/item_lists/{item_list_id}"

    username: str
    item_list_id: str


class BoothArtistUrl(ArtistUrl, BoothUrl):
    normalization = "https://{username}.booth.pm"  # TODO: fix this

    username: str | None
    user_id: int | None


class BoothImageUrl(PostAssetUrl, BoothUrl):
    item_id: int


class BoothProfileImageUrl(PostAssetUrl, BoothUrl):
    user_id: int | None
    # user_uuid: str | None
