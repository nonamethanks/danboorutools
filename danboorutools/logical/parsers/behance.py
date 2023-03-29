from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.behance import BehanceArtistUrl, BehancePostUrl, BehanceUrl
from danboorutools.models.url import UselessUrl


class BehanceNetParser(UrlParser):
    reserved_names = ["for_you", "galleries", "live", "gallery", "careers", "blog", "99u", "misc", "search"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BehanceUrl | UselessUrl | None:  # type: ignore[return]
        if parsable_url.subdomain == "help":
            return UselessUrl(parsed_url=parsable_url)

        match parsable_url.url_parts:
            # https://www.behance.net/gallery/83538125/The-Saiyan-Prince-Pitch
            # https://www.behance.net/gallery/41416703/F-A-N-A-R-T/modules/249943521
            case "gallery", post_id, title, *_rest if post_id.isnumeric():
                return BehancePostUrl(parsed_url=parsable_url,
                                      post_id=int(post_id),
                                      title=title)

            # http://www.behance.net/sparklingthunder
            # https://www.behance.net/kienphongtran/sourcefiles
            case username, *_rest if username not in cls.reserved_names:
                return BehanceArtistUrl(parsed_url=parsable_url,
                                        username=username)

            case _:
                return None
