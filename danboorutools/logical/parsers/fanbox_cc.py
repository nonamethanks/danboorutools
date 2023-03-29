from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.fanbox import FanboxArtistUrl, FanboxImageUrl, FanboxPostUrl, FanboxUrl


class FanboxCcParser(UrlParser):
    test_cases = {
        FanboxArtistUrl: [
            "https://www.fanbox.cc/@tsukiori",

            "https://omu001.fanbox.cc",
            "https://omu001.fanbox.cc/posts",
            "https://omu001.fanbox.cc/plans",
        ],
        FanboxImageUrl: [
            "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png",
            "https://downloads.fanbox.cc/images/post/39714/c/1200x630/JvjJal8v1yLgc5DPyEI05YpT.jpeg",
            "https://downloads.fanbox.cc/images/post/39714/w/1200/JvjJal8v1yLgc5DPyEI05YpT.jpeg",
        ],
        FanboxPostUrl: [
            "https://www.fanbox.cc/@tsukiori/posts/1080657",

            "https://omu001.fanbox.cc/posts/39714",
            "https://brllbrll.fanbox.cc/posts/626093",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FanboxUrl | None:
        if parsable_url.subdomain in ["www", ""]:
            return cls._match_username_in_path(parsable_url)
        elif parsable_url.subdomain == "downloads":
            return cls._match_image(parsable_url)
        else:
            return cls._match_username_in_subdomain(parsable_url)

    @staticmethod
    def _match_username_in_path(parsable_url: ParsableUrl) -> FanboxUrl | None:
        match parsable_url.url_parts:
            # https://www.fanbox.cc/@tsukiori/posts/1080657
            case username, "posts", post_id:
                return FanboxPostUrl(parsed_url=parsable_url,
                                     username=username.removeprefix("@"),
                                     post_id=int(post_id))

            # https://www.fanbox.cc/@tsukiori
            case username, *_:
                return FanboxArtistUrl(parsed_url=parsable_url,
                                       username=username.removeprefix("@"))

            case _:
                return None

    @staticmethod
    def _match_username_in_subdomain(parsable_url: ParsableUrl) -> FanboxUrl | None:
        match parsable_url.url_parts:
            # https://omu001.fanbox.cc/posts/39714"
            # https://brllbrll.fanbox.cc/posts/626093",  # R18
            case "posts", post_id:
                return FanboxPostUrl(parsed_url=parsable_url,
                                     username=parsable_url.subdomain,
                                     post_id=int(post_id))

            # https://omu001.fanbox.cc
            # https://omu001.fanbox.cc/posts
            # https://omu001.fanbox.cc/plans
            case _:
                return FanboxArtistUrl(parsed_url=parsable_url,
                                       username=parsable_url.subdomain.removeprefix("@"))

    @staticmethod
    def _match_image(parsable_url: ParsableUrl) -> FanboxImageUrl | None:
        # https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png
        # https://downloads.fanbox.cc/images/post/39714/c/1200x630/JvjJal8v1yLgc5DPyEI05YpT.jpeg
        # https://downloads.fanbox.cc/images/post/39714/w/1200/JvjJal8v1yLgc5DPyEI05YpT.jpeg
        match parsable_url.url_parts:
            case "images", "post", post_id, *_, _filename:
                return FanboxImageUrl(parsed_url=parsable_url,
                                      post_id=int(post_id),
                                      image_type="post",
                                      pixiv_id=None)

            case _:
                return None
