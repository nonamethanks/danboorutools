from __future__ import annotations

from typing import TYPE_CHECKING

from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.piapro import PiaproArtistUrl, PiaproPostUrl, PiaproUrl
from danboorutools.models.url import UselessUrl

if TYPE_CHECKING:
    from danboorutools.models.url import Url


class PiaproJpParser(UrlParser):
    RESERVED_NAMES = ["t", "music", "illust", "text", "collabo_list",
                      "official_collabo", "intro", "static", "upload_step",
                      "login", "my_page", "follow", "user", "content_list", "jump"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:

            # https://piapro.jp/t/Z8xi
            # http://piapro.jp/content/7vmui67vj0uabnoc
            case ("t" | "content") as post_type, post_id:
                return PiaproPostUrl(parsed_url=parsable_url,
                                     post_id=post_id,
                                     post_type=post_type)

            # http://piapro.jp/t/01ix/20161127225144
            case "t", post_id, _timestamp:
                return PiaproPostUrl(parsed_url=parsable_url,
                                     post_id=post_id,
                                     post_type="t")

            # http://piapro.jp/a/content/?id=ncdt0qjsdpdb0lrk
            case "a", "content":
                return PiaproPostUrl(parsed_url=parsable_url,
                                     post_id=parsable_url.query["id"],
                                     post_type="content")

            # https://piapro.jp/jump/?url=https%3A%2F%2Fitoiss.tumblr.com
            case "jump", :
                url = parsable_url.query["url"]
                return cls.parse(url)

            # http://piapro.jp/ooyuko29
            case username, :
                if username not in cls.RESERVED_NAMES:
                    return PiaproArtistUrl(parsed_url=parsable_url,
                                           username=username)

                else:
                    return UselessUrl(parsed_url=parsable_url)

            case "pages", "official_collabo", *_:
                raise UnparsableUrlError(parsable_url)

            case ("timg" | "thumb_i"), *_:
                raise UnparsableUrlError(parsable_url)  # can't be arsed rn

            case _:
                return None
