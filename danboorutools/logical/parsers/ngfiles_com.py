from danboorutools.logical.extractors.newgrounds import NewgroundsAssetUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NgfilesComParser(UrlParser):
    test_cases = {
        NewgroundsAssetUrl: [
            "https://art.ngfiles.com/images/1254000/1254722_natthelich_pandora.jpg",
            "https://art.ngfiles.com/images/1033000/1033622_natthelich_fire-emblem-marth-plus-progress-pic.png?f1569487181",

            "https://art.ngfiles.com/thumbnails/1254000/1254985.png?f1588263349",

            "https://art.ngfiles.com/comments/57000/iu_57615_7115981.jpg",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NewgroundsAssetUrl | None:
        match parsable_url.url_parts:
            case ("images" | "thumbnails"), _, filename:
                instance = NewgroundsAssetUrl(parsable_url)

                if "_" in filename:
                    _, username, title = filename.split("_")
                    instance.title = title
                    instance.username = username
                else:
                    instance.title = None
                    instance.username = None

            case "comments", _, _:
                instance = NewgroundsAssetUrl(parsable_url)
                instance.title = None
                instance.username = None

            case _:
                return None

        return instance
