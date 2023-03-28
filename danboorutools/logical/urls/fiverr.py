from danboorutools.models.url import ArtistUrl, PostUrl, RedirectUrl, Url


class FiverrUrl(Url):
    pass


class FiverrArtistUrl(ArtistUrl, FiverrUrl):
    artist_name: str

    normalize_template = "https://www.fiverr.com/{artist_name}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.artist_name]

    @property
    def related(self) -> list[Url]:
        return []


class FiverrPostUrl(PostUrl, FiverrUrl):
    post_title: str
    artist_name: str

    normalize_template = "https://www.fiverr.com/{artist_name}/{post_title}"

    @property
    def gallery(self) -> FiverrArtistUrl:
        return FiverrArtistUrl.build(artist_name=self.artist_name)


class FiverrShareUrl(RedirectUrl, FiverrUrl):
    subdir: str
    share_code: str

    normalize_template = "https://www.fiverr.com/{subdir}/{share_code}"

# class FiverrImageUrl(PostAssetUrl, FiverrUrl):
#     pass
# https://fiverr-res.cloudinary.com/images/q_auto,f_auto/gigs/260079434/original/d389a825502252500d21fc78928e7bc6dd7c1e49/draw-you-anime-waifu.jpeg
# https://fiverr-res.cloudinary.com/images/gigs/260079434/original/d389a825502252500d21fc78928e7bc6dd7c1e49/draw-you-anime-waifu.jpeg
