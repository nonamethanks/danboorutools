from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.mastodon import (MastodonArtistUrl, MastodonImageUrl, MastodonOauthUrl, MastodonOldImageUrl,
                                                       MastodonPostUrl, MastodonUrl)
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class XxxXxxParser(UrlParser):
    domains = ["pawoo.net", "baraag.net"]

    test_cases = {
        MastodonArtistUrl: [
            "https://pawoo.net/@evazion",
            "https://baraag.net/@danbooru",
            "https://baraag.net/@quietvice/media",
            "https://baraag.net/web/@loodncrood",
            "https://pawoo.net/users/esoraneko",
            "https://pawoo.net/users/khurata/media",
            "https://pawoo.net/web/accounts/47806",
            "https://baraag.net/web/accounts/107862785324786980",
        ],
        MastodonPostUrl: [
            "https://pawoo.net/@evazion/19451018",
            "https://baraag.net/@curator/102270656480174153",
            "https://pawoo.net/web/statuses/19451018",
            "https://pawoo.net/web/statuses/19451018/favorites",
            "https://baraag.net/web/statuses/102270656480174153",
        ],
        MastodonImageUrl: [
            "https://img.pawoo.net/media_attachments/files/001/297/997/small/c4272a09570757c2.png",
            "https://img.pawoo.net/media_attachments/files/001/297/997/original/c4272a09570757c2.png",
            "https://baraag.net/system/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4",
            "https://media.baraag.net/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4",
        ],
        MastodonOldImageUrl: [
            "https://pawoo.net/media/lU2uV7C1MMQSb1czwvg",
        ],
        MastodonOauthUrl: [
            "https://pawoo.net/oauth_authentications/25289748",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MastodonUrl | None:
        if parsable_url.url_parts[0] in ["media_attachments", "system", "media"]:
            return cls._match_asset(parsable_url)
        else:
            return cls._match_everything_else(parsable_url)

    @staticmethod
    def _match_asset(parsable_url: ParsableUrl) -> MastodonUrl | None:
        instance: MastodonUrl
        match parsable_url.url_parts:
            case "media_attachments", "files", *subdirs, _, _filename:
                instance = MastodonImageUrl(parsable_url)
                instance.subdirs = subdirs

            case "system", "media_attachments", "files", *subdirs, _, _filename:
                instance = MastodonImageUrl(parsable_url)
                instance.subdirs = subdirs

            case "media", filename:
                instance = MastodonOldImageUrl(parsable_url)
                instance.filename = filename

            case _:
                return None

        instance.site = parsable_url.domain
        return instance

    @staticmethod
    def _match_everything_else(parsable_url: ParsableUrl) -> MastodonUrl | None:
        instance: MastodonUrl

        match parsable_url.url_parts:
            case username, post_id if post_id.isnumeric() and username.startswith("@"):
                instance = MastodonPostUrl(parsable_url)
                instance.username = username.removeprefix("@")
                instance.post_id = int(post_id)

            case username, *_ if username.startswith("@"):
                instance = MastodonArtistUrl(parsable_url)
                instance.username = username.removeprefix("@")

            case "web", username, *_ if username.startswith("@"):
                instance = MastodonArtistUrl(parsable_url)
                instance.username = username.removeprefix("@")

            case "users", username, *_:
                instance = MastodonArtistUrl(parsable_url)
                instance.username = username

            case "web", "statuses", post_id, *_:
                instance = MastodonPostUrl(parsable_url)
                instance.username = None
                instance.post_id = int(post_id)

            case "web", "accounts", user_id, *_:
                instance = MastodonArtistUrl(parsable_url)
                instance.username = None
                instance.user_id = int(user_id)

            case "oauth_authentications", oauth_id:
                instance = MastodonOauthUrl(parsable_url)
                instance.oauth_id = int(oauth_id)

            case "interact", _:  # ???? https://baraag.net/interact/106315841367726753
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        instance.site = parsable_url.domain
        return instance
