from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class NicovideoOekakiUrl(Url):
    pass


class NicovideoOekakiPostUrl(PostUrl, NicovideoOekakiUrl):
    post_id: int


class NicovideoOekakiArtistUrl(ArtistUrl, NicovideoOekakiUrl):
    user_id: int


class NicovideoOekakiImageUrl(PostAssetUrl, NicovideoOekakiUrl):
    post_id: int
