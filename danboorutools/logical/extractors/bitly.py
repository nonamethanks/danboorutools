from danboorutools.models.url import RedirectUrl


class BitlyUrl(RedirectUrl):
    redirect_id: str

    normalize_string = "https://bit.ly/{redirect_id}"
