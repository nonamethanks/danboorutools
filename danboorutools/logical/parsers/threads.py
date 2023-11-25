from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.threads import ThreadsArtistUrl, ThreadsPostUrl, ThreadsUrl


class ThreadsNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ThreadsUrl | None:
        match parsable_url.url_parts:
            # https://www.threads.net/@mawari5577
            case username, if username.startswith("@"):
                return ThreadsArtistUrl(parsed_url=parsable_url,
                                        username=username.removeprefix("@"))

            # https://www.threads.net/@kohane.leona08/post/CuWHfdFSa7P
            # https://www.threads.net/@saikou.jp/post/CvX2h-wJCTe.jpg
            case username, "post", post_id if username.startswith("@"):
                return ThreadsPostUrl(parsed_url=parsable_url,
                                      username=username.removeprefix("@"),
                                      post_id=post_id.split(".")[0])
            case _:
                return None
