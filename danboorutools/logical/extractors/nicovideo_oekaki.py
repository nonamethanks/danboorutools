from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class NicovideoOekakiUrl(Url):
    pass


class NicovideoOekakiPostUrl(PostUrl, NicovideoOekakiUrl):
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://dic.nicovideo.jp/oekaki_id/{kwargs['post_id']}"


class NicovideoOekakiArtistUrl(ArtistUrl, NicovideoOekakiUrl):
    user_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://dic.nicovideo.jp/u/{kwargs['user_id']}"


class NicovideoOekakiImageUrl(PostAssetUrl, NicovideoOekakiUrl):
    post_id: int

    @property
    def full_size(self) -> str:
        return f"https://dic.nicovideo.jp/oekaki/{self.post_id}.{self.parsed_url.extension}"
