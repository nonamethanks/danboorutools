from danboorutools.logical.extractors.anifty import AniftyArtistUrl, AniftyPostUrl, AniftyTokenUrl, AniftyUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class AniftyJpParser(UrlParser):
    test_cases = {
        AniftyPostUrl: [
            "https://anifty.jp/creations/373",
            "https://anifty.jp/ja/creations/373",
            "https://anifty.jp/zh/creations/373",
            "https://anifty.jp/zh-Hant/creations/373",
        ],
        AniftyArtistUrl: [
            "https://anifty.jp/@hightree",
            "https://anifty.jp/ja/@hightree",
        ],
        AniftyTokenUrl: [
            "https://anifty.jp/tokens/17",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AniftyUrl | None:
        instance: AniftyUrl
        match parsable_url.url_parts:
            case *_, "creations", post_id:
                instance = AniftyPostUrl(parsable_url)
                instance.post_id = int(post_id)
            case *_, username if username.startswith("@"):
                instance = AniftyArtistUrl(parsable_url)
                instance.username = username.removeprefix("@")
            case *_, "tokens", token_id:
                instance = AniftyTokenUrl(parsable_url)
                instance.token_id = int(token_id)
            case _:
                return None
        return instance
