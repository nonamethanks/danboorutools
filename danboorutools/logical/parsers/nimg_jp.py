from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.nicoseiga import NicoSeigaImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NimgJpParser(UrlParser):
    test_cases = {
        NicoSeigaImageUrl: [
            "https://dcdn.cdn.nimg.jp/priv/62a56a7f67d3d3746ae5712db9cac7d465f4a339/1592186183/10466669",
            "https://dcdn.cdn.nimg.jp/nicoseiga/lohas/o/8ba0a9b2ea34e1ef3b5cc50785bd10cd63ec7e4a/1592187477/10466669",
            # https://dcdn.cdn.nimg.jp/niconews/articles/body_images/5544288/5b4672e6da49c2dd195a95caca424c20ff8f67f9b23cc6689fc28719de4c6037b3839d2d8757ceb8e25cfd6ce98093d71101831bbfc39e26baaca915ce32633d
            # https://img.cdn.nimg.jp/s/nicovideo/thumbnails/39681749/39681749.7860892.original/r1280x720l?key=8bc8ebb87e7286cef4e3303bb32e15b93e99c959e9fe4ce2af66884a4167024a  # -> https://www.nicovideo.jp/watch/sm39681749
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NicoSeigaImageUrl | None:
        match parsable_url.url_parts:
            case "priv", _, _, image_id:
                instance = NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id)
                instance.image_type = None

            case "nicoseiga", "lohas", "o", _, _, image_id:
                instance = NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id[:-1])
                instance.image_type = None

            case "niconews", *_:
                raise UnparsableUrl(parsable_url)

            case _, "nicovideo", *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
