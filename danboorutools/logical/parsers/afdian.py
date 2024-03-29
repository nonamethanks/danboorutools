from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.afdian import AfdianArtistImageUrl, AfdianArtistUrl, AfdianImageUrl, AfdianPostUrl, AfdianUrl


class AfdianNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AfdianUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:

            # https://afdian.net/p/8d419ad28b3511ed830452540025c377
            case "p", post_id:
                return AfdianPostUrl(parsed_url=parsable_url,
                                     post_id=post_id)

            # https://afdian.net/a/mgong520
            case "a", username:
                return AfdianArtistUrl(parsed_url=parsable_url,
                                       username=username)

            # https://afdian.net/@gggmmm
            case username, if username.startswith("@"):
                return AfdianArtistUrl(parsed_url=parsable_url,
                                       username=username[1:])

            case _:
                return None


class AfdiancdnComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AfdianUrl | None:
        match parsable_url.url_parts:

            # https://pic1.afdiancdn.com/user/8440cb74b10f11edb7ee52540025c377/common/e3e98041bbe0123906b4e949083616e7_w357_h357_s172.jpg?imageView2/3/w/320/h/180
            # https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/common/9dcd4e26f34d248a945e083570cf96f5_w2508_h3541_s3529.png
            # https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/common/54c2aa732a3c1783b73fba1e2149f56d_w1170_h2532_s5894.png?imageView2/1/w/1500/h/400  # background artist image
            case "user", user_id, "common", _:
                return AfdianImageUrl(parsed_url=parsable_url,
                                      user_id=user_id)

            # https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/avatar/b8affcddfae89977b4ea2f48cf4a6513_w5715_h3775_s1932.png?imageView2/1/w/120/h/120
            case "user", user_id, "avatar", _:
                return AfdianArtistImageUrl(parsed_url=parsable_url,
                                            user_id=user_id)

            case _:
                return None
