from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class TinamiUrl(Url):
    pass


class TinamiPostUrl(PostUrl, TinamiUrl):
    post_id: int

    normalize_template = "https://www.tinami.com/view/{post_id}"


class TinamiComicUrl(PostUrl, TinamiUrl):
    comic_id: int
    comic_title: str

    normalize_template = "https://www.tinami.com/comic/{comic_title}/{comic_id}"


class TinamiArtistUrl(ArtistUrl, TinamiUrl):
    profile_id: int | None
    user_id: int | None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if user_id := kwargs.get("user_id"):
            return f"https://www.tinami.com/creator/profile/{user_id}"
        elif profile_id := kwargs.get("profile_id"):
            return f"https://www.tinami.com/profile/{profile_id}"
        else:
            raise NotImplementedError


class TinamiImageUrl(PostAssetUrl, TinamiUrl):
    ...
