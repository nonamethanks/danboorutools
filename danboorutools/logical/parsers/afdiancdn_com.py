from danboorutools.logical.extractors.afdian import AfdianArtistImageUrl, AfdianImageUrl, AfdianUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class AfdiancdnComParser(UrlParser):

    test_cases = {
        AfdianImageUrl: [
            "https://pic1.afdiancdn.com/user/8440cb74b10f11edb7ee52540025c377/common/e3e98041bbe0123906b4e949083616e7_w357_h357_s172.jpg?imageView2/3/w/320/h/180",
            "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/common/9dcd4e26f34d248a945e083570cf96f5_w2508_h3541_s3529.png",
            "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/common/54c2aa732a3c1783b73fba1e2149f56d_w1170_h2532_s5894.png?imageView2/1/w/1500/h/400"  # background artist image
        ],
        AfdianArtistImageUrl: [
            "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/avatar/b8affcddfae89977b4ea2f48cf4a6513_w5715_h3775_s1932.png?imageView2/1/w/120/h/120",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AfdianUrl | None:
        instance: AfdianUrl
        match parsable_url.url_parts:
            case "user", user_id, "common", _:
                instance = AfdianImageUrl(parsable_url)
                instance.user_id = user_id
            case "user", user_id, "avatar", _:
                instance = AfdianArtistImageUrl(parsable_url)
                instance.user_id = user_id
            case _:
                return None

        return instance
