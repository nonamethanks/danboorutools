from danboorutools.logical.extractors import nicoseiga as ns
from danboorutools.logical.extractors import nicovideo as nv
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NicoMs(UrlParser):
    test_cases = {
        nv.NicovideoVideoUrl: [
            "https://nico.ms/nm36465441",
            "https://nico.ms/sm36465441",
        ],
        ns.NicoSeigaIllustUrl: [
            "https://nico.ms/im10922621",
        ],
        ns.NicoSeigaMangaUrl: [
            "https://nico.ms/mg310193",
        ],
        nv.NicovideoCommunityUrl: [
            "http://nico.ms/co2744246",
        ],
        nv.NicovideoArtistUrl: [
            "http://nico.ms/user/43606505",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> nv.NicovideoUrl | ns.NicoSeigaUrl | None:
        instance: nv.NicovideoUrl | ns.NicoSeigaUrl

        if len(parsable_url.url_parts) == 1:
            match (_id := parsable_url.url_parts[0])[:2]:
                case "im":
                    instance = ns.NicoSeigaIllustUrl(parsable_url)
                    instance.illust_id = int(_id[2:])
                case "mg":
                    instance = ns.NicoSeigaMangaUrl(parsable_url)
                    instance.manga_id = int(_id[2:])
                case ("sm" | "nm"):
                    instance = nv.NicovideoVideoUrl(parsable_url)
                    instance.video_id = _id
                case "co":
                    instance = nv.NicovideoCommunityUrl(parsable_url)
                    instance.community_id = int(_id[2:])

                case _:
                    return None
        else:
            match parsable_url.url_parts:
                case "user", user_id:
                    instance = nv.NicovideoArtistUrl(parsable_url)
                    instance.user_id = int(user_id)
                case _:
                    return None

        return instance
