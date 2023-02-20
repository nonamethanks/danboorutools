from danboorutools.logical.extractors.deviantart import DeviantArtArtistUrl, DeviantArtImageUrl, DeviantArtPostUrl, DeviantArtUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class DeviantartComParser(UrlParser):
    test_cases = {
        DeviantArtPostUrl: [
            "https://www.deviantart.com/deviation/685436408",

            "https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408",
            "https://www.deviantart.com/bellhenge/art/788000274",

            "https://noizave.deviantart.com/art/test-post-please-ignore-685436408",
            "https://framboosi.deviantart.com/art/Wendy-commision-for-x4blade-133926691?q=gallery%3Aframboosi%2F12287691\u0026qo=81",
            "https://www.deviantart.com/wickellia/art/Anneliese-839666684#comments",
        ],
        DeviantArtImageUrl: [
            "http://www.deviantart.com/download/135944599/Touhou___Suwako_Moriya_Colored_by_Turtle_Chibi.png",
            "https://www.deviantart.com/download/549677536/countdown_to_midnight_by_kawacy-d939hwg.jpg?token=92090cd3910d52089b566661e8c2f749755ed5f8&ts=1438535525",
        ],

        DeviantArtArtistUrl: [
            "https://www.deviantart.com/noizave",
            "https://deviantart.com/noizave",
            "https://www.deviantart.com/nlpsllp/gallery",

            "https://noizave.deviantart.com",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtUrl | None:
        if parsable_url.subdomain in ["", "www"]:
            return cls._match_username_in_path(parsable_url)
        else:
            return cls._match_username_in_subdomain(parsable_url)

    @staticmethod
    def _match_username_in_path(parsable_url: ParsableUrl) -> DeviantArtUrl | None:
        instance: DeviantArtUrl
        match parsable_url.url_parts:
            # https://www.deviantart.com/deviation/685436408
            case "deviation", deviation_id:
                instance = DeviantArtPostUrl(parsable_url)
                instance.deviation_id = int(deviation_id)
                instance.username = None
                instance.title = None

            # http://www.deviantart.com/download/135944599/Touhou___Suwako_Moriya_Colored_by_Turtle_Chibi.png
            # https://www.deviantart.com/download/549677536/countdown_to_midnight_by_kawacy-d939hwg.jpg?token=92090cd3910d52089b566661e8c2f749755ed5f8&ts=1438535525
            case "download", deviation_id, filename:
                instance = DeviantArtImageUrl(parsable_url)
                instance.deviation_id = int(deviation_id)
                instance.parse_filename(filename)

            # https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408
            # https://www.deviantart.com/bellhenge/art/788000274
            # https://www.deviantart.com/wickellia/art/Anneliese-839666684#comments
            case username, "art", title:
                instance = DeviantArtPostUrl(parsable_url)
                if "-" in title:
                    [instance.title, deviation_id] = title.rsplit("-", maxsplit=1)
                else:
                    instance.title = None
                    deviation_id = title
                try:
                    instance.deviation_id = int(deviation_id)
                except ValueError:
                    instance.deviation_id = int(deviation_id.split("#")[0])
                instance.username = username

            # https://www.deviantart.com/noizave
            # https://deviantart.com/noizave
            # https://www.deviantart.com/nlpsllp/gallery
            case username, *_:
                instance = DeviantArtArtistUrl(parsable_url)
                instance.username = username

            case _:
                return None

        return instance

    @staticmethod
    def _match_username_in_subdomain(parsable_url: ParsableUrl) -> DeviantArtUrl | None:
        instance: DeviantArtUrl
        match parsable_url.url_parts:
            # https://noizave.deviantart.com/art/test-post-please-ignore-685436408
            # https://framboosi.deviantart.com/art/Wendy-commision-for-x4blade-133926691?q=gallery%3Aframboosi%2F12287691\u0026qo=81
            case "art", title:
                instance = DeviantArtPostUrl(parsable_url)
                [instance.title, deviation_id] = title.rsplit("-", maxsplit=1)
                instance.deviation_id = int(deviation_id)
                instance.username = parsable_url.subdomain

            # https://noizave.deviantart.com
            case _:
                instance = DeviantArtArtistUrl(parsable_url)
                instance.username = parsable_url.subdomain

        return instance
