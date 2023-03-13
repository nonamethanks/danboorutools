from danboorutools.models.url import InfoUrl


class CarrdUrl(InfoUrl):
    username: str

    normalize_template = "https://{username}.carrd.co"
