from danboorutools.logical.extractors.afdian import AfdianArtistUrl, AfdianPostUrl, AfdianUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class AfdianNetParser(UrlParser):
    test_cases = {
        AfdianArtistUrl: [
            "https://afdian.net/a/mgong520",
            "https://afdian.net/@gggmmm",
        ],
        AfdianPostUrl: [
            "https://afdian.net/p/8d419ad28b3511ed830452540025c377",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AfdianUrl | None:
        instance: AfdianUrl
        match parsable_url.url_parts:
            case "p", post_id:
                instance = AfdianPostUrl(parsable_url)
                instance.post_id = post_id
            case "a", username:
                instance = AfdianArtistUrl(parsable_url)
                instance.username = username
            case username, if username.startswith("@"):
                instance = AfdianArtistUrl(parsable_url)
                instance.username = username[1:]
            case _:
                return None

        return instance
