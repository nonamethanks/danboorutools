from danboorutools.models.url import InfoUrl


class OdaibakoUrl(InfoUrl):
    username: str

    normalize_template = "https://odaibako.net/u/{username}"
