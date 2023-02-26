from ward import test

from danboorutools.models.url import Url

urls = {
    "https://pawoo.net/@evazion": "https://pawoo.net/@evazion",
    "https://baraag.net/@danbooru": "https://baraag.net/@danbooru",
    "https://baraag.net/@quietvice/media": "https://baraag.net/@quietvice",
    "https://baraag.net/web/@loodncrood": "https://baraag.net/@loodncrood",
    "https://pawoo.net/users/esoraneko": "https://pawoo.net/@esoraneko",
    "https://pawoo.net/users/khurata/media": "https://pawoo.net/@khurata",
    "https://pawoo.net/web/accounts/47806": "https://pawoo.net/web/accounts/47806",
    "https://baraag.net/web/accounts/107862785324786980": "https://baraag.net/web/accounts/107862785324786980",

    "https://pawoo.net/@evazion/19451018": "https://pawoo.net/@evazion/19451018",
    "https://baraag.net/@curator/102270656480174153": "https://baraag.net/@curator/102270656480174153",
    "https://pawoo.net/web/statuses/19451018": "https://pawoo.net/web/statuses/19451018",
    "https://pawoo.net/web/statuses/19451018/favorites": "https://pawoo.net/web/statuses/19451018",
    "https://baraag.net/web/statuses/102270656480174153": "https://baraag.net/web/statuses/102270656480174153",

    "https://img.pawoo.net/media_attachments/files/001/297/997/small/c4272a09570757c2.png": "https://img.pawoo.net/media_attachments/files/001/297/997/original/c4272a09570757c2.png",
    "https://img.pawoo.net/media_attachments/files/001/297/997/original/c4272a09570757c2.png": "https://img.pawoo.net/media_attachments/files/001/297/997/original/c4272a09570757c2.png",
    "https://baraag.net/system/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4": "https://baraag.net/system/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4",
    "https://media.baraag.net/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4": "https://media.baraag.net/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4",
    "https://pawoo.net/media/lU2uV7C1MMQSb1czwvg": "https://pawoo.net/media/lU2uV7C1MMQSb1czwvg",

    "https://pawoo.net/oauth_authentications/25289748": "https://pawoo.net/oauth_authentications/25289748",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @ test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
