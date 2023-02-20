from danboorutools.logical.extractors.nicoseiga import NicoSeigaImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NicomangaJpParser(UrlParser):
    test_cases = {
        NicoSeigaImageUrl: [
            "https://deliver.cdn.nicomanga.jp/thumb/7891081p?1590171867",
            "https://drm.cdn.nicomanga.jp/image/d4a2faa68ec34f95497db6601a4323fde2ccd451_9537/8017978p?1570012695",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NicoSeigaImageUrl | None:
        match parsable_url.url_parts:
            case "thumb", image_id if image_id.endswith("p"):
                instance = NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id[:-1])
                instance.image_type = None

            case "image", _, image_id if image_id.endswith("p"):
                instance = NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id[:-1])
                instance.image_type = None

            case _:
                return None

        return instance
