from danboorutools.logical.extractors.plurk import PlurkArtistUrl, PlurkImageUrl, PlurkPostUrl, PlurkUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class PlurkComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PlurkUrl | None:
        instance: PlurkUrl

        match parsable_url.url_parts:
            # https://www.plurk.com/p/om6zv4
            # https://www.plurk.com/m/p/okxzae
            case *_, "p", post_id:
                instance = PlurkPostUrl(parsable_url)
                instance.post_id = post_id

            # https://www.plurk.com/u/ddks2923
            # https://www.plurk.com/m/u/leiy1225
            # https://www.plurk.com/s/u/salmonroe13
            case *_, "u", username:
                instance = PlurkArtistUrl(parsable_url)
                instance.username = username

            # https://www.plurk.com/m/redeyehare
            case "m", username:
                instance = PlurkArtistUrl(parsable_url)
                instance.username = username

            # https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg
            # https://images.plurk.com/mx_5wj6WD0r6y4rLN0DL3sqag.jpg
            case _filename, if parsable_url.subdomain == "images":
                instance = PlurkImageUrl(parsable_url)
                instance.image_id = parsable_url.stem.removeprefix("mx_")

            # https://www.plurk.com/redeyehare
            # https://www.plurk.com/RSSSww/invite/4
            case username, *_:
                instance = PlurkArtistUrl(parsable_url)
                instance.username = username

            case _:
                return None

        return instance
