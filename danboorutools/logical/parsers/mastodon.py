from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import mastodon as m
from danboorutools.models.url import UselessUrl


class MastodonParser(UrlParser):
    domains = ["pawoo.net", "baraag.net", "mstdn.jp"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> m.MastodonUrl | None:
        if parsable_url.url_parts[0] in ["media_attachments", "system", "media"]:
            return cls._match_asset(parsable_url)
        else:
            return cls._match_everything_else(parsable_url)

    @staticmethod
    def _match_asset(parsable_url: ParsableUrl) -> m.MastodonUrl | None:
        match parsable_url.url_parts:
            # https://img.pawoo.net/media_attachments/files/001/297/997/small/c4272a09570757c2.png
            # https://img.pawoo.net/media_attachments/files/001/297/997/original/c4272a09570757c2.png
            # https://media.baraag.net/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4
            case "media_attachments", "files", *subdirs, _, _filename:
                return m.MastodonImageUrl(parsed_url=parsable_url,
                                          site=parsable_url.domain,
                                          subdirs=subdirs)

            # https://baraag.net/system/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4
            case "system", "media_attachments", "files", *subdirs, _, _filename:
                return m.MastodonImageUrl(parsed_url=parsable_url,
                                          site=parsable_url.domain,
                                          subdirs=subdirs)

            # https://pawoo.net/media/lU2uV7C1MMQSb1czwvg
            case "media", filename:
                return m.MastodonOldImageUrl(parsed_url=parsable_url,
                                             site=parsable_url.domain,
                                             filename=filename)

            case _:
                return None

    @staticmethod
    def _match_everything_else(parsable_url: ParsableUrl) -> m.MastodonUrl | UselessUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://pawoo.net/@evazion/19451018
            # https://baraag.net/@curator/102270656480174153
            case username, post_id if post_id.isnumeric() and username.startswith("@"):
                return m.MastodonPostUrl(parsed_url=parsable_url,
                                         username=username.removeprefix("@"),
                                         site=parsable_url.domain,
                                         post_id=int(post_id))

            # https://pawoo.net/@evazion
            # https://baraag.net/@danbooru
            # https://baraag.net/@quietvice/media
            case username, *_ if username.startswith("@"):
                return m.MastodonArtistUrl(parsed_url=parsable_url,
                                           site=parsable_url.domain,
                                           username=username.removeprefix("@"))

            # https://baraag.net/web/@loodncrood
            case "web", username, *_ if username.startswith("@"):
                return m.MastodonArtistUrl(parsed_url=parsable_url,
                                           site=parsable_url.domain,
                                           username=username.removeprefix("@"))

            # https://baraag.net/users/Butterchalk/statuses/110020463245055611/activity
            case "users", username, "statuses", post_id, *_rest if post_id.isnumeric():
                return m.MastodonPostUrl(parsed_url=parsable_url,
                                         username=username.removeprefix("@"),
                                         site=parsable_url.domain,
                                         post_id=int(post_id))

            # https://pawoo.net/users/esoraneko
            # https://pawoo.net/users/khurata/media
            case "users", username, *_:
                return m.MastodonArtistUrl(parsed_url=parsable_url,
                                           site=parsable_url.domain,
                                           username=username)

            # https://pawoo.net/web/statuses/19451018
            # https://pawoo.net/web/statuses/19451018/favorites
            # https://baraag.net/web/statuses/102270656480174153
            case "web", "statuses", post_id, *_:
                return m.MastodonPostUrl(parsed_url=parsable_url,
                                         username=None,
                                         site=parsable_url.domain,
                                         post_id=int(post_id))

            # https://pawoo.net/web/accounts/47806
            # https://baraag.net/web/accounts/107862785324786980
            case "web", "accounts", user_id, *_:
                return m.MastodonWebIdUrl(parsed_url=parsable_url,
                                          site=parsable_url.domain,
                                          user_id=int(user_id))

            # https://pawoo.net/oauth_authentications/25289748
            case "oauth_authentications", oauth_id:
                return m.MastodonOauthUrl(parsed_url=parsable_url,
                                          site=parsable_url.domain,
                                          oauth_id=int(oauth_id))

            case "interact", _:  # ???? https://baraag.net/interact/106315841367726753
                raise UnparsableUrlError(parsable_url)

            case "tags", *_:
                return UselessUrl(parsed_url=parsable_url)

            case _:
                return None
