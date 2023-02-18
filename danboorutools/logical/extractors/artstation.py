from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class ArtStationUrl(Url):
    pass


class ArtStationOldPostUrl(RedirectUrl, ArtStationUrl):
    # https://www.artstation.com/artwork/cody-from-sf  # (old; redirects to https://www.artstation.com/artwork/3JJA)
    post_title: str


class ArtStationPostUrl(PostUrl, ArtStationUrl):
    post_id: str
    username: str | None


class ArtStationArtistUrl(ArtistUrl, ArtStationUrl):
    username: str
    normalization = "https://www.artstation.com/{username}"


class ArtStationImageUrl(PostAssetUrl, ArtStationUrl):
    filename: str


class ArtStationMarketplacePostUrl(PostUrl, ArtStationUrl):
    post_id: str
    normalization = "https://www.artstation.com/marketplace/p/{post_id}"
