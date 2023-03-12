from danboorutools.models.url import ArtistUrl, PostUrl, Url


class BcyUrl(Url):
    pass


class BcyArtistUrl(ArtistUrl, BcyUrl):
    user_id: int

    normalize_string = "https://bcy.net/u/{user_id}"


class BcyPostUrl(PostUrl, BcyUrl):
    post_id: int

    normalize_string = "https://bcy.net/item/detail/{post_id}"


class OldBcyPostUrl(PostUrl, BcyUrl):
    first_id: int
    second_id: int

    normalize_string = "http://bcy.net/illust/detail/{first_id}/{second_id}"

    is_deleted = True
