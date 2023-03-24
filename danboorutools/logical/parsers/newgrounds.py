from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls import newgrounds as ns


class NewgroundsComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NewgroundsUrl | None:
        instance: ns.NewgroundsUrl
        match parsable_url.url_parts:
            # https://www.newgrounds.com/art/view/puddbytes/costanza-at-bat
            # https://www.newgrounds.com/art/view/natthelich/fire-emblem-marth-plus-progress-pic
            case "art", "view", username, title:
                instance = ns.NewgroundsPostUrl(parsable_url)
                instance.username = username
                instance.title = title

            # https://www.newgrounds.com/portal/video/536659 # (curl 'https://www.newgrounds.com/portal/video/536659' - H 'X-Requested-With: XMLHttpRequest')
            # https://www.newgrounds.com/portal/view/536659
            case "portal", ("video" | "view"), video_id:
                instance = ns.NewgroundsVideoPostUrl(parsable_url)
                instance.video_id = int(video_id)

            # https://www.newgrounds.com/dump/item/ff72b3c77a959a8cca07f92d28f5d6ce
            # https://www.newgrounds.com/dump/download/ff72b3c77a959a8cca07f92d28f5d6ce
            case "dump", ("item" | "download"), dump_id:
                instance = ns.NewgroundsDumpUrl(parsable_url)
                instance.dump_id = dump_id

            # https://natthelich.newgrounds.com
            # https://natthelich.newgrounds.com/art/
            case _ if parsable_url.subdomain not in ["", "www"]:
                instance = ns.NewgroundsArtistUrl(parsable_url)
                instance.username = parsable_url.subdomain

            case _:
                return None

        return instance


class NgfilesComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NewgroundsAssetUrl | None:
        match parsable_url.url_parts:
            case ("images" | "thumbnails"), _, filename:
                instance = ns.NewgroundsAssetUrl(parsable_url)

                # https://art.ngfiles.com/images/1254000/1254722_natthelich_pandora.jpg
                # https://art.ngfiles.com/images/1033000/1033622_natthelich_fire-emblem-marth-plus-progress-pic.png?f1569487181
                if "_" in filename:
                    _, username, title = filename.split("_")
                    instance.title = title
                    instance.username = username

                # https://art.ngfiles.com/thumbnails/1254000/1254985.png?f1588263349
                else:
                    instance.title = None
                    instance.username = None

            # https://art.ngfiles.com/comments/57000/iu_57615_7115981.jpg
            case "comments", _, _:
                instance = ns.NewgroundsAssetUrl(parsable_url)
                instance.title = None
                instance.username = None

            case _:
                return None

        return instance


class UngroundedNetParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NewgroundsAssetUrl | None:
        match parsable_url.url_parts:
            # https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.1080p.mp4?1639666238
            # https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.720p.mp4?1639666238
            # https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.360p.mp4?1639666238
            case "alternate", _, _:
                instance = ns.NewgroundsAssetUrl(parsable_url)
                instance.title = None
                instance.username = None
            case _:
                return None

        return instance
