from danboorutools.models.url import InfoUrl


class CarrdUrl(InfoUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        username = kwargs["username"]
        return f"https://{username}.carrd.co"
