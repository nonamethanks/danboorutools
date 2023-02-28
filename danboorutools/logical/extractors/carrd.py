from danboorutools.models.url import InfoUrl


class CarrdUrl(InfoUrl):
    username: str

    normalize_string = "https://{username}.carrd.co"
