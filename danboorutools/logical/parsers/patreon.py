from danboorutools.logical.extractors.patreon import PatreonArtistUrl, PatreonImageUrl, PatreonPostUrl, PatreonUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class PatreonComParser(UrlParser):
    RESERVED_NAMES = {"home", "join", "posts", "login", "signup", "search",
                      "messages", "logout", "policies", "policy", "hc", "user", "bePatron"}

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PatreonUrl | None:
        instance: PatreonUrl
        match parsable_url.url_parts:
            # https://patreon.com/posts/22819080
            # https://www.patreon.com/posts/nino-13608041
            case "posts", title_and_id:
                instance = PatreonPostUrl(parsable_url)
                if "-" in title_and_id:
                    instance.title, _, post_id = title_and_id.rpartition("-")
                else:
                    instance.title = None
                    post_id = title_and_id
                instance.post_id = int(post_id)
            # https://www.patreon.com/oughta/posts
            case username, ("creators" | "posts" | "overview") if username not in cls.RESERVED_NAMES:
                instance = PatreonArtistUrl(parsable_url)
                instance.username = username
            # http://www.patreon.com/koshio/
            # https://www.patreon.com/Sirk/creators
            case username, if username not in cls.RESERVED_NAMES:
                instance = PatreonArtistUrl(parsable_url)
                instance.username = username
            # https://www.patreon.com/user?u=4993143
            case "user", *_:
                instance = PatreonArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["u"])
                instance.username = None
            # https://www.patreon.com/m/Alamander820
            case "m", username:
                instance = PatreonArtistUrl(parsable_url)
                instance.username = username
            # https://www.patreon.com/join/lindaroze/checkout?rid=318429\u0026redirect_uri=%2Fposts%2Fpapi-and-suu-28718113
            case "join", username, "checkout" if "redirect_uri" in parsable_url.query:
                instance = PatreonPostUrl(parsable_url)
                instance.title, _, post_id = parsable_url.query["redirect_uri"].split("/")[-1].rpartition("-")
                instance.post_id = int(post_id)
                instance.username = username
            # https://www.patreon.com/join/thirdphp?
            case "join", username:
                instance = PatreonArtistUrl(parsable_url)
                instance.username = username
            # https://cdn3.patreon.com/1/patreon.posts/8488601187679302177.jpg?v=3JKW77OaAo4mC9Tak_CnHRb1MR4-sz0fMaTQRLhlajY%3D
            # https://c3.patreon.com/2/patreon-posts/2475253990789383424.png?t=1498176000\u0026v=MwaSWLQaHk67s25L9kOPZwTMeyhxnuNVXFqOBIQWuXA%3D
            # https://c10.patreon.com/3/e30%3D/patreon-posts/3L5OtwNuetsk4HajgipG91z7_d-5wAn07awsvd9yJWjAI4_O4ghzS90k2OSfiqCA.jpg?token-time=1502409600\u0026token-hash=aHjY4qz5GqNu3sQ5_AAHa3vApAsEfMCRi_Agxi5I1sM%3D
            # https://c3.patreon.com/2/patreon.user/Xw9EBuJAeV0Xh360JZzYT1KaQx1svrgqL9AfIx9ZVhHSRTEJmMyqGHu5l26Jazsw_large_2.png?t=1494853451\u0026w=1920\u0026v=qXwa0ugy4NEFLvLMNPa4421H44YdNXni5Ur1HcIU3d4%3D
            case *_, ("patreon.posts" | "patreon-posts" | "patreon.user"), _:
                instance = PatreonImageUrl(parsable_url)
            # https://www.patreon.com/bePatron?c=170214\u0026rid=218676\u0026redirect_uri=/posts/makoto-nanaya-8366347
            case "bePatron", if "redirect_uri" in parsable_url.query:
                instance = PatreonPostUrl(parsable_url)
                instance.title, _, post_id = parsable_url.query["redirect_uri"].split("/")[-1].rpartition("-")
                instance.post_id = int(post_id)
            case _:
                return None

        return instance


class PatreonusercontentComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PatreonUrl | None:
        match parsable_url.url_parts:
            # https://c10.patreonusercontent.com/4/patreon-media/p/post/73164326/0b437130a504407e9cddbe57b575f4d0/eyJxIjoxMDAsIndlYnAiOjB9/1.png?token-time=1668729600\u0026token-hash=cRKqb666VduPfE04ZnUQYOwkl8gWcfcJakWMrqHCUOI=
            case _, "patreon-media", "p", "post", post_id, *_:
                instance = PatreonImageUrl(parsable_url)
                instance.post_id = int(post_id)

            # https://c10.patreonusercontent.com/3/eyJ3Ijo2MjB9/patreon-media/p/post/36495392/cb0702f66b4945d5adaf3fcd98d0f077/1.jpg?token-time=1591617419\u0026token-hash=C9E0pBzAiL4iKHiRhv98Otv2rXfd0ay5-hSGp6ahdZ8=
            case _, _, "patreon-media", "p", "post", post_id, *_:
                instance = PatreonImageUrl(parsable_url)
                instance.post_id = int(post_id)

            # https://c10.patreonusercontent.com/3/e30%3D/patreon-posts/o2-s3ubiq-rvQgJVTMlI4-_djsAXvF_YiV2LSEKkpv9sTxqhDKo9-WboTju_sjTU.png?token-time=1506470400\u0026token-hash=htqRR_7JryCMoDqgyknNFqfRWrejuahP16JKwWnaUrA%3D
            case *_, "patreon-posts", _:
                instance = PatreonImageUrl(parsable_url)

            case _:
                return None

        return instance
