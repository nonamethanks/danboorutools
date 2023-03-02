from danboorutools.logical.extractors.patreon import PatreonArtistUrl, PatreonImageUrl, PatreonPostUrl, PatreonUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class PatreonComParser(UrlParser):
    RESERVED_NAMES = {"home", "join", "posts", "login", "signup", "search",
                      "messages", "logout", "policies", "policy", "hc", "user", "bePatron"}

    test_cases = {
        PatreonArtistUrl: [
            "https://www.patreon.com/user?u=4993143",
            "http://www.patreon.com/koshio/",
            "https://www.patreon.com/Sirk/creators",
            "https://www.patreon.com/join/thirdphp?",
            "https://www.patreon.com/m/Alamander820",
            "https://www.patreon.com/oughta/posts",
        ],
        PatreonPostUrl: [
            "https://patreon.com/posts/22819080",
            "https://www.patreon.com/posts/nino-13608041",
            "https://www.patreon.com/join/lindaroze/checkout?rid=318429\u0026redirect_uri=%2Fposts%2Fpapi-and-suu-28718113",
            "https://www.patreon.com/bePatron?c=170214\u0026rid=218676\u0026redirect_uri=/posts/makoto-nanaya-8366347",
        ],
        PatreonImageUrl: [
            "https://cdn3.patreon.com/1/patreon.posts/8488601187679302177.jpg?v=3JKW77OaAo4mC9Tak_CnHRb1MR4-sz0fMaTQRLhlajY%3D",
            "https://c3.patreon.com/2/patreon-posts/2475253990789383424.png?t=1498176000\u0026v=MwaSWLQaHk67s25L9kOPZwTMeyhxnuNVXFqOBIQWuXA%3D",
            "https://c10.patreon.com/3/e30%3D/patreon-posts/3L5OtwNuetsk4HajgipG91z7_d-5wAn07awsvd9yJWjAI4_O4ghzS90k2OSfiqCA.jpg?token-time=1502409600\u0026token-hash=aHjY4qz5GqNu3sQ5_AAHa3vApAsEfMCRi_Agxi5I1sM%3D",
            "https://c3.patreon.com/2/patreon.user/Xw9EBuJAeV0Xh360JZzYT1KaQx1svrgqL9AfIx9ZVhHSRTEJmMyqGHu5l26Jazsw_large_2.png?t=1494853451\u0026w=1920\u0026v=qXwa0ugy4NEFLvLMNPa4421H44YdNXni5Ur1HcIU3d4%3D",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PatreonUrl | None:
        instance: PatreonUrl
        match parsable_url.url_parts:
            case "posts", title_and_id:
                instance = PatreonPostUrl(parsable_url)
                if "-" in title_and_id:
                    instance.title, _, post_id = title_and_id.rpartition("-")
                else:
                    instance.title = None
                    post_id = title_and_id
                instance.post_id = int(post_id)
            case username, ("creators" | "posts" | "overview") if username not in cls.RESERVED_NAMES:
                instance = PatreonArtistUrl(parsable_url)
                instance.username = username
            case username, if username not in cls.RESERVED_NAMES:
                instance = PatreonArtistUrl(parsable_url)
                instance.username = username
            case "user", *_:
                instance = PatreonArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.params["u"])
                instance.username = None
            case "m", username:
                instance = PatreonArtistUrl(parsable_url)
                instance.username = username
            case "join", username, "checkout" if "redirect_uri" in parsable_url.params:
                instance = PatreonPostUrl(parsable_url)
                instance.title, _, post_id = parsable_url.params["redirect_uri"].partition("%2F")[-1].partition("-")
                instance.post_id = int(post_id)
                instance.username = username
            case "join", username:
                instance = PatreonArtistUrl(parsable_url)
                instance.username = username
            case *_, ("patreon.posts" | "patreon-posts" | "patreon.user"), _:
                instance = PatreonImageUrl(parsable_url)
            case "bePatron", if "redirect_uri" in parsable_url.params:
                instance = PatreonPostUrl(parsable_url)
                instance.title, _, post_id = parsable_url.params["redirect_uri"].partition("/")[-1].partition("-")
                instance.post_id = int(post_id)
            case _:
                return None

        return instance
