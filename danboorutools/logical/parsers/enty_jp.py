from danboorutools.logical.extractors.enty import EntyArtistImageUrl, EntyArtistUrl, EntyImageUrl, EntyPostUrl, EntyUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser

RESERVED_NAMES = ["blogs", "en", "messages", "posts", "products", "ranking",
                  "search", "series", "service_navigations", "signout", "titles", "users"]


class EntyJpParser(UrlParser):
    test_cases = {
        EntyPostUrl: [
            "https://enty.jp/posts/141598?ref=newest_post_pc",
            "https://enty.jp/en/posts/141598?ref=newest_post_pc",
        ],
        EntyArtistUrl: [
            "https://enty.jp/kouyoumatsunaga?active_tab=posts#2",
            "https://enty.jp/en/kouyoumatsunaga?active_tab=posts#2",
            "https://enty.jp/users/4932",
        ],
        EntyImageUrl: [
            "https://img01.enty.jp/uploads/post/thumbnail/141598/post_show_b6c7d85c-b63c-4950-9152-e4bf30678022.png",
            "https://img01.enty.jp/uploads/ckeditor/pictures/194353/content_20211227_130_030_100.png",
        ],
        EntyArtistImageUrl: [
            "https://img01.enty.jp/uploads/entertainer/wallpaper/2044/post_show_enty_top.png",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EntyUrl | None:
        instance: EntyUrl
        match parsable_url.url_parts:
            case "uploads", ("post" | "ckeditor"), ("thumbnail" | "pictures"), post_id, _:
                instance = EntyImageUrl(parsable_url)
                instance.post_id = int(post_id)
            case "uploads", "entertainer", "wallpaper", user_id, _:
                instance = EntyArtistImageUrl(parsable_url)
                instance.user_id = int(user_id)
            case *_, "posts", post_id:
                instance = EntyPostUrl(parsable_url)
                instance.post_id = int(post_id)
            case "users", user_id:
                instance = EntyArtistUrl(parsable_url)
                instance.username = None
                instance.user_id = int(user_id)
            case ("en" | "ja"), username if username not in RESERVED_NAMES:
                instance = EntyArtistUrl(parsable_url)
                instance.username = username
                instance.user_id = None
            case [username] if username not in RESERVED_NAMES:
                instance = EntyArtistUrl(parsable_url)
                instance.username = username
                instance.user_id = None
            case _:
                return None
        return instance
