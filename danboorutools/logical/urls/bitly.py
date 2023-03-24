from danboorutools.models.url import RedirectUrl


class BitlyUrl(RedirectUrl):
    redirect_id: str

    normalize_template = "https://bit.ly/{redirect_id}"
