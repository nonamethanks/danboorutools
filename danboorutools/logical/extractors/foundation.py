from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class FoundationUrl(Url):
    pass


class FoundationPostUrl(PostUrl, FoundationUrl):
    username: str
    collection: str
    post_id: int

    normalize_string = "https://foundation.app/@{username}/{collection}/{post_id}"


class FoundationArtistUrl(ArtistUrl, FoundationUrl):
    username: str | None
    user_hash: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        if (username := kwargs.get("username")):
            return f"https://foundation.app/@{username}"
        elif (user_hash := kwargs['user_hash']):
            return f"https://foundation.app/{user_hash}"
        else:
            raise ValueError


class FoundationImageUrl(PostAssetUrl, FoundationUrl):
    file_hash: str | None
    work_id: int | None
    token_id: str | None

    @property
    def full_size(self) -> str:
        if self.file_hash:
            return f"https://f8n-ipfs-production.imgix.net/{self.file_hash}/nft.{self.parsed_url.extension}"
        elif self.parsed_url.hostname == "f8n-production-collection-assets.imgix.net" and self.token_id and self.work_id:
            return f"https://f8n-production-collection-assets.imgix.net/{self.token_id}/{self.work_id}/nft.{self.parsed_url.extension}"
        else:
            return self.parsed_url.url_without_query
