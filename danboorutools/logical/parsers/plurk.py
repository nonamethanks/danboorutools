from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.plurk import PlurkArtistUrl, PlurkImageUrl, PlurkPostUrl, PlurkUrl


class PlurkComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PlurkUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://www.plurk.com/p/om6zv4
            # https://www.plurk.com/m/p/okxzae
            case *_, "p", post_id:
                return PlurkPostUrl(parsed_url=parsable_url,
                                    post_id=post_id)

            # https://www.plurk.com/u/ddks2923
            # https://www.plurk.com/m/u/leiy1225
            # https://www.plurk.com/s/u/salmonroe13
            case *_, "u", username:
                return PlurkArtistUrl(parsed_url=parsable_url,
                                      username=username)

            # https://www.plurk.com/m/redeyehare
            case "m", username:
                return PlurkArtistUrl(parsed_url=parsable_url,
                                      username=username)

            # https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg
            # https://images.plurk.com/mx_5wj6WD0r6y4rLN0DL3sqag.jpg
            case _filename, if parsable_url.subdomain == "images":
                return PlurkImageUrl(parsed_url=parsable_url,
                                     image_id=parsable_url.stem.removeprefix("mx_"))

            # https://www.plurk.com/redeyehare
            # https://www.plurk.com/RSSSww/invite/4
            case username, *_:
                return PlurkArtistUrl(parsed_url=parsable_url,
                                      username=username)

            case _:
                return None
