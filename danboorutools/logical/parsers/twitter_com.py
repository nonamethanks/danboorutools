from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.twitter import (TwitterArtistUrl, TwitterIntentUrl, TwitterOnlyStatusUrl, TwitterPostUrl,
                                                      TwitterShortenerUrl, TwitterUrl)
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class TwitterComParser(UrlParser):
    test_cases = {
        TwitterArtistUrl: [
            "https://twitter.com/intent/user?screen_name=ryuudog_NFT",
            "https://twitter.com/motty08111213",
            "https://twitter.com/motty08111213/likes",
        ],
        TwitterPostUrl: [
            "https://twitter.com/motty08111213/status/943446161586733056",
            "https://twitter.com/motty08111213/status/943446161586733056?s=19",
            "https://twitter.com/Kekeflipnote/status/1496555599718498319/video/1",
            "https://twitter.com/sato_1_11/status/1496489742791475201/photo/2",
            "https://twitter.com/i/web/status/943446161586733056",
            "https://twitter.com/i/status/943446161586733056",
        ],
        TwitterOnlyStatusUrl: [
            "https://twitter.com/intent/favorite?tweet_id=1300476511254753280",
        ],
        TwitterIntentUrl: [
            "https://twitter.com/i/user/889592953",
            "https://twitter.com/intent/user?user_id=2819289818",
        ],
        TwitterShortenerUrl: [
            "https://pic.twitter.com/Dxn7CuVErW",
        ]

    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TwitterUrl | None:
        instance: TwitterUrl
        match parsable_url.url_parts:
            case username, *_, "status", post_id:
                if username == "i":
                    instance = TwitterOnlyStatusUrl(parsable_url)
                    instance.post_id = int(post_id.removesuffix("#m"))
                else:
                    instance = TwitterPostUrl(parsable_url)
                    instance.username = username
                    instance.post_id = int(post_id.removesuffix("#m"))
            case username, "status", post_id, *_:
                if username == "i":
                    instance = TwitterOnlyStatusUrl(parsable_url)
                    instance.post_id = int(parsable_url.params["tweet_id"])
                else:
                    instance = TwitterPostUrl(parsable_url)
                    instance.username = username
                    instance.post_id = int(post_id)
            case shortener_id, if parsable_url.subdomain == "pic":
                instance = TwitterShortenerUrl(parsable_url)
                instance.shortener_id = shortener_id
            case username, *_ if username not in ["home", "i", "intent", "search"]:
                instance = TwitterArtistUrl(parsable_url)
                instance.username = username
            case "i", "user", user_id:
                instance = TwitterIntentUrl(parsable_url)
                instance.intent_id = int(user_id)
            case "intent", "user" if "user_id" in parsable_url.params:
                instance = TwitterIntentUrl(parsable_url)
                instance.intent_id = int(parsable_url.params["user_id"])
            case "intent", "user" if "screen_name" in parsable_url.params:
                instance = TwitterArtistUrl(parsable_url)
                instance.username = parsable_url.params["screen_name"]
            case "intent", "favorite":
                instance = TwitterOnlyStatusUrl(parsable_url)
                instance.post_id = int(parsable_url.params["tweet_id"])

            case ("home" | "search"), *_:
                raise UnparsableUrl(parsable_url)

            case "i", "timeline":
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
