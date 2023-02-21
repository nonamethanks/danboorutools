from danboorutools.logical.extractors.plurk import PlurkArtistUrl, PlurkImageUrl, PlurkPostUrl, PlurkUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class PlurkComParser(UrlParser):
    test_cases = {
        PlurkArtistUrl: [
            "https://www.plurk.com/m/redeyehare",
            "https://www.plurk.com/u/ddks2923",
            "https://www.plurk.com/m/u/leiy1225",
            "https://www.plurk.com/s/u/salmonroe13",
            "https://www.plurk.com/redeyehare",
            "https://www.plurk.com/RSSSww/invite/4",
        ],
        PlurkImageUrl: [
            "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg",
            "https://images.plurk.com/mx_5wj6WD0r6y4rLN0DL3sqag.jpg",
        ],
        PlurkPostUrl: [
            "https://www.plurk.com/p/om6zv4",
            "https://www.plurk.com/m/p/okxzae",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PlurkUrl | None:
        instance: PlurkUrl

        match parsable_url.url_parts:
            case *_, "p", post_id:
                instance = PlurkPostUrl(parsable_url)
                instance.post_id = post_id
            case *_, "u", username:
                instance = PlurkArtistUrl(parsable_url)
                instance.username = username
            case "m", username:
                instance = PlurkArtistUrl(parsable_url)
                instance.username = username
            case filename, if parsable_url.subdomain == "images":
                instance = PlurkImageUrl(parsable_url)
                instance.image_id = filename.split(".")[0].removeprefix("mx_")
            case username, *_:
                instance = PlurkArtistUrl(parsable_url)
                instance.username = username
            case _:
                return None

        return instance
