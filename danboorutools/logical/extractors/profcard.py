from danboorutools.models.url import Url


class ProfcardUrl(Url):
    user_id: str

    normalize_template = "https://profcard.info/u/{user_id}"
