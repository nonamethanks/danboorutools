from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.nicoseiga import NicoSeigaImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NicoseigaJpParser(UrlParser):
    test_cases = {
        NicoSeigaImageUrl: [
            "https://lohas.nicoseiga.jp/o/971eb8af9bbcde5c2e51d5ef3a2f62d6d9ff5552/1589933964/3583893",  # https://seiga.nicovideo.jp/seiga/im3583893

            "https://lohas.nicoseiga.jp/priv/b80f86c0d8591b217e7513a9e175e94e00f3c7a1/1384936074/3583893",  # https://seiga.nicovideo.jp/seiga/im3583893
            "https://lohas.nicoseiga.jp/priv/3521156?e=1382558156&h=f2e089256abd1d453a455ec8f317a6c703e2cedf",  # https://seiga.nicovideo.jp/seiga/im3521156
            "https://lohas.nicoseiga.jp/thumb/2163478i",  # https://seiga.nicovideo.jp/seiga/im2163478
            "https://lohas.nicoseiga.jp/thumb/1591081q",  # https://seiga.nicovideo.jp/seiga/im1591081
            "https://lohas.nicoseiga.jp/thumb/4744553p",  # https://seiga.nicovideo.jp/watch/mg122274

            # https://lohas.nicoseiga.jp/material/5746c5/4459092?
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NicoSeigaImageUrl | None:
        match parsable_url.url_parts:
            case "o", _, _, illust_id:
                instance = NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(illust_id)
                instance.image_type = "illust"

            case "priv", *_, image_id:
                instance = NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id)
                instance.image_type = None

            case "thumb", illust_id if illust_id.endswith("i") or illust_id.endswith("q"):
                instance = NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(illust_id[:-1])
                instance.image_type = "illust"

            case "thumb", image_id if image_id.endswith("p"):
                instance = NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id[:-1])
                instance.image_type = None

            case "material", *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
