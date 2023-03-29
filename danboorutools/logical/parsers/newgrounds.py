from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import newgrounds as ns


class NewgroundsComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NewgroundsUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://www.newgrounds.com/art/view/puddbytes/costanza-at-bat
            # https://www.newgrounds.com/art/view/natthelich/fire-emblem-marth-plus-progress-pic
            case "art", "view", username, title:
                return ns.NewgroundsPostUrl(parsed_url=parsable_url,
                                            username=username,
                                            title=title)

            # https://www.newgrounds.com/portal/video/536659 # (curl 'https://www.newgrounds.com/portal/video/536659' - H 'X-Requested-With: XMLHttpRequest')
            # https://www.newgrounds.com/portal/view/536659
            case "portal", ("video" | "view"), video_id:
                return ns.NewgroundsVideoPostUrl(parsed_url=parsable_url,
                                                 video_id=int(video_id))

            # https://www.newgrounds.com/dump/item/ff72b3c77a959a8cca07f92d28f5d6ce
            # https://www.newgrounds.com/dump/download/ff72b3c77a959a8cca07f92d28f5d6ce
            case "dump", ("item" | "download"), dump_id:
                return ns.NewgroundsDumpUrl(parsed_url=parsable_url,
                                            dump_id=dump_id)

            # https://natthelich.newgrounds.com
            # https://natthelich.newgrounds.com/art/
            case _ if parsable_url.subdomain not in ["", "www"]:
                return ns.NewgroundsArtistUrl(parsed_url=parsable_url,
                                              username=parsable_url.subdomain)

            case _:
                return None


class NgfilesComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NewgroundsAssetUrl | None:
        match parsable_url.url_parts:
            case ("images" | "thumbnails"), _, filename:
                # https://art.ngfiles.com/images/1254000/1254722_natthelich_pandora.jpg
                # https://art.ngfiles.com/images/1033000/1033622_natthelich_fire-emblem-marth-plus-progress-pic.png?f1569487181
                if "_" in filename:
                    _, username, title = filename.split("_")

                # https://art.ngfiles.com/thumbnails/1254000/1254985.png?f1588263349
                else:
                    title = None
                    username = None

                return ns.NewgroundsAssetUrl(parsed_url=parsable_url,
                                             title=title,
                                             username=username)

            # https://art.ngfiles.com/comments/57000/iu_57615_7115981.jpg
            case "comments", _, _:
                return ns.NewgroundsAssetUrl(parsed_url=parsable_url,
                                             title=None,
                                             username=None)

            case _:
                return None


class UngroundedNetParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NewgroundsAssetUrl | None:
        match parsable_url.url_parts:
            # https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.1080p.mp4?1639666238
            # https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.720p.mp4?1639666238
            # https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.360p.mp4?1639666238
            case "alternate", _, _:
                return ns.NewgroundsAssetUrl(parsed_url=parsable_url,
                                             title=None,
                                             username=None)

            case _:
                return None
