from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import postype as p


class PostypeComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> p.PostypeUrl | None:
        if parsable_url.subdomain in ("www", ""):
            return cls._match_no_subdomain(parsable_url)
        elif parsable_url.subdomain in ("i", "c3"):
            return cls._match_image_subdomain(parsable_url)
        else:
            return cls._match_subdomain(parsable_url)

    @staticmethod
    def _match_no_subdomain(parsable_url: ParsableUrl) -> p.PostypeUrl | None:
        match parsable_url.url_parts:
            # https://www.postype.com/@luland/post/16389638
            case username, "post", post_id if username.startswith("@"):
                return p.PostypePostUrl(parsed_url=parsable_url,
                                        post_id=int(post_id),
                                        username=username)

            # https://www.postype.com/@luland/
            case username, if username.startswith("@"):
                return p.PostypeArtistUrl(parsed_url=parsable_url,
                                          username=username)

            # https://www.postype.com/profile/@6qyflt
            case "profile", user_id if user_id.startswith("@"):
                return p.PostypeBadArtistUrl(parsed_url=parsable_url,
                                             user_id=user_id)

            # https://www.postype.com/profile/@efuki0/posts
            case "profile", user_id, "posts" if user_id.startswith("@"):
                return p.PostypeBadArtistUrl(parsed_url=parsable_url,
                                             user_id=user_id)

            case _:
                return None

    @staticmethod
    def _match_image_subdomain(parsable_url: ParsableUrl) -> p.PostypeUrl | None:
        match parsable_url.url_parts:
            # http://i.postype.com/2016/12/27/01/52/0a88e4fef1f92974d3834511120492c8.png?w=1000
            case _y, _m, _d, _h, _mm, _hash:
                return p.PostypeImageUrl(parsed_url=parsable_url)
            case _:
                return None

    @staticmethod
    def _match_subdomain(parsable_url: ParsableUrl) -> p.PostypeUrl | None:
        match parsable_url.url_parts:

            case "post", post_id:
                return p.PostypePostUrl(parsed_url=parsable_url,
                                        post_id=int(post_id),
                                        username=parsable_url.subdomain)

            # https://purple-blur.postype.com/series/949574/%EC%86%8C%EB%8B%89%EB%A7%8C%ED%99%94%EC%97%B0%EC%84%B1
            case "series", series_id, *_:
                return p.PostypeSeriesUrl(parsed_url=parsable_url,
                                          username=parsable_url.subdomain,
                                          series_id=int(series_id))

            # https://peonrin.postype.com/series
            case ("series" | "posts"), :
                return p.PostypeArtistUrl(parsed_url=parsable_url,
                                          username=parsable_url.subdomain)

            # https://muacmm.postype.com/
            case []:
                return p.PostypeArtistUrl(parsed_url=parsable_url,
                                          username=parsable_url.subdomain)

            case _:
                return None
