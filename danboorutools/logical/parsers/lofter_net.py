from danboorutools.logical.extractors.lofter import LofterArtistUrl, LofterPostUrl, LofterUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class LofterComParser(UrlParser):

    test_cases = {
        LofterArtistUrl: [
            "https://www.lofter.com/front/blog/home-page/noshiqian",
            "http://www.lofter.com/app/xiaokonggedmx",
            "http://www.lofter.com/blog/semblance",
            "http://gengar563.lofter.com",
        ],
        LofterPostUrl: [
            "https://gengar563.lofter.com/post/1e82da8c_1c98dae1b",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LofterUrl | None:
        instance: LofterUrl
        if parsable_url.subdomain in ["www", "i"] or not parsable_url.subdomain:
            match parsable_url.url_parts:
                case ("app" | "blog"), username:
                    instance = LofterArtistUrl(parsable_url)
                    instance.username = username
                case "front", "blog", "home-page", username:
                    instance = LofterArtistUrl(parsable_url)
                    instance.username = username
                case _:
                    return None
        else:
            match parsable_url.url_parts:
                case "post", post_id:
                    instance = LofterPostUrl(parsable_url)
                    instance.username = parsable_url.subdomain
                    instance.post_id = post_id
                case _:
                    instance = LofterArtistUrl(parsable_url)
                    instance.username = parsable_url.subdomain

        return instance
