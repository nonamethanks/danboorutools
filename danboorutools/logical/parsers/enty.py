from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.enty import EntyArtistImageUrl, EntyArtistUrl, EntyImageUrl, EntyPostUrl, EntyUrl

RESERVED_NAMES = {"blogs", "en", "messages", "posts", "products", "ranking",
                  "search", "series", "service_navigations", "signout", "titles", "users"}


class EntyJpParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EntyUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://img01.enty.jp/uploads/post/thumbnail/141598/post_show_b6c7d85c-b63c-4950-9152-e4bf30678022.png
            # https://img01.enty.jp/uploads/ckeditor/pictures/194353/content_20211227_130_030_100.png
            case "uploads", ("post" | "ckeditor"), ("thumbnail" | "pictures"), post_id, _:
                return EntyImageUrl(parsed_url=parsable_url,
                                    post_id=int(post_id))

            # https://img01.enty.jp/uploads/entertainer/wallpaper/2044/post_show_enty_top.png
            case "uploads", "entertainer", "wallpaper", user_id, _:
                return EntyArtistImageUrl(parsed_url=parsable_url,
                                          user_id=int(user_id))

            # https://enty.jp/posts/141598?ref=newest_post_pc
            # https://enty.jp/en/posts/141598?ref=newest_post_pc
            case *_, "posts", post_id:
                return EntyPostUrl(parsed_url=parsable_url,
                                   post_id=int(post_id))

            # https://enty.jp/users/4932
            case "users", user_id:
                return EntyArtistUrl(parsed_url=parsable_url,
                                     username=None,
                                     user_id=int(user_id))

            # https://enty.jp/en/kouyoumatsunaga?active_tab=posts#2
            case ("en" | "ja"), username if username not in RESERVED_NAMES:
                return EntyArtistUrl(parsed_url=parsable_url,
                                     username=username,
                                     user_id=None)

            # https://enty.jp/kouyoumatsunaga?active_tab=posts#2
            case username, if username not in RESERVED_NAMES:
                return EntyArtistUrl(parsed_url=parsable_url,
                                     username=username,
                                     user_id=None)

            case _:
                return None
