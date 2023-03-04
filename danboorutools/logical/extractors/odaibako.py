from danboorutools.models.url import InfoUrl


class OdaibakoUrl(InfoUrl):
    username: str

    normalize_string = "https://odaibako.net/u/{username}"
