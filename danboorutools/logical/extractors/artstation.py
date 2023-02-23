from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class ArtStationUrl(Url):
    pass


class ArtStationOldPostUrl(RedirectUrl, ArtStationUrl):
    # https://www.artstation.com/artwork/cody-from-sf  # (old; redirects to https://www.artstation.com/artwork/3JJA)
    post_title: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_title = kwargs["post_title"]
        return f"https://www.artstation.com/artwork/{post_title}"


class ArtStationPostUrl(PostUrl, ArtStationUrl):
    post_id: str
    username: str | None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        username = kwargs.get("username")
        post_id = kwargs["post_id"]
        if username:
            return f"https://{username}.artstation.com/projects/{post_id}"
        else:
            return f"https://www.artstation.com/artwork/{post_id}"


class ArtStationArtistUrl(ArtistUrl, ArtStationUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        username = kwargs["username"]
        return f"https://www.artstation.com/{username}"


class ArtStationImageUrl(PostAssetUrl, ArtStationUrl):
    filename: str
    asset_type: str
    asset_subdirs: str

    @property
    def full_size(self) -> str:
        if self.parsed_url.subdomain == "cdn-animation":
            return f"https://cdn-animation.artstation.com/p/{self.asset_type}/{self.asset_subdirs}/{self.filename}"
        else:
            return f"https://cdn.artstation.com/p/assets/{self.asset_type}/images/{self.asset_subdirs}/4k/{self.filename}"
        # https://cdn.artstation.com/p/assets/covers/images/007/262/828/4k/monica-kyrie-1.jpg this is actually wrong, the original is "original"
        # idk how to properly fix this


class ArtStationMarketplacePostUrl(PostUrl, ArtStationUrl):
    post_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        return f"https://www.artstation.com/marketplace/p/{post_id}"
