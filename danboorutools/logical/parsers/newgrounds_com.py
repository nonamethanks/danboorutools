from danboorutools.logical.extractors.newgrounds import (NewgroundsArtistUrl, NewgroundsDumpUrl, NewgroundsPostUrl, NewgroundsUrl,
                                                         NewgroundsVideoPostUrl)
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NewgroundsComParser(UrlParser):
    test_cases = {
        NewgroundsArtistUrl: [
            "https://natthelich.newgrounds.com",
            "https://natthelich.newgrounds.com/art/",
        ],
        NewgroundsPostUrl: [
            "https://www.newgrounds.com/art/view/puddbytes/costanza-at-bat",
            "https://www.newgrounds.com/art/view/natthelich/fire-emblem-marth-plus-progress-pic",
        ],
        NewgroundsVideoPostUrl: [
            # (curl 'https://www.newgrounds.com/portal/video/536659' - H 'X-Requested-With: XMLHttpRequest')
            "https://www.newgrounds.com/portal/video/536659",
            "https://www.newgrounds.com/portal/view/536659",
        ],
        NewgroundsDumpUrl: [
            "https://www.newgrounds.com/dump/item/ff72b3c77a959a8cca07f92d28f5d6ce",
            "https://www.newgrounds.com/dump/download/ff72b3c77a959a8cca07f92d28f5d6ce",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NewgroundsUrl | None:
        instance: NewgroundsUrl
        match parsable_url.url_parts:
            case "art", "view", username, title:
                instance = NewgroundsPostUrl(parsable_url)
                instance.username = username
                instance.title = title

            case "portal", ("video" | "view"), video_id:
                instance = NewgroundsVideoPostUrl(parsable_url)
                instance.video_id = int(video_id)

            case "dump", ("item" | "download"), dump_id:
                instance = NewgroundsDumpUrl(parsable_url)
                instance.dump_id = dump_id

            case _ if parsable_url.subdomain not in ["", "www"]:
                instance = NewgroundsArtistUrl(parsable_url)
                instance.username = parsable_url.subdomain

            case _:
                return None

        return instance
