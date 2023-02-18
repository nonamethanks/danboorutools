from danboorutools.models.url import InfoUrl


class CarrdUrl(InfoUrl):
    username: str

    normalization = "https://{username}.carrd.co"
