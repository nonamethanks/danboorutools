from danboorutools.models.url import ArtistUrl, GalleryUrl, PostUrl, RedirectUrl, Url


class FacebookUrl(Url):
    pass


class FacebookUserUrl(ArtistUrl, FacebookUrl):
    username: str

    normalize_template = "https://www.facebook.com/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []  # for normal users, not pages, it's simply not worth it


class FacebookPageUrl(RedirectUrl, FacebookUrl):
    page_name: str
    page_id: int

    normalize_template = "https://www.facebook.com/pages/{page_name}/{page_id}"


class FacebookOldPageUrl(RedirectUrl, FacebookUrl):
    old_id: str
    category: str

    normalize_template = "https://www.facebook.com/pages/category/{category}/{old_id}"


class FacebookOldPeopleUrl(RedirectUrl, FacebookUrl):
    people_id: str

    normalize_template = "https://www.facebook.com/profile.php?id={people_id}"


class FacebookPeopleUrl(ArtistUrl, FacebookUrl):
    people_name: str
    people_id: str

    normalize_template = "https://www.facebook.com/people/{people_name}/{people_id}"


class FacebookPostUrl(PostUrl, FacebookUrl):
    post_id: str
    username: str

    normalize_template = "https://www.facebook.com/{username}/posts/{post_id}"


class FacebookMediaSetUrl(PostUrl, FacebookUrl):
    media_set_id: str

    normalize_template = "https://www.facebook.com/media/set/?set={media_set_id}"


class FacebookGroupUrl(GalleryUrl, FacebookUrl):
    group_id: str

    normalize_template = "https://www.facebook.com/groups/{group_id}"
