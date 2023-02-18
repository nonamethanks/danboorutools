from danboorutools.logical.extractors.ehentai import EHentaiImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class HathNetworkParser(UrlParser):
    test_cases = {
        EHentaiImageUrl: [
            "https://ijmwujr.grduyvrrtxiu.hath.network:40162/h/5bf1c8b26c4d0d35951b7116d151209f6784420e-137816-810-1228-jpg/keystamp=1676307900-1fa0db7a58;fileindex=120969163;xres=2400/4134835_103198602_p0.jpg",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EHentaiImageUrl | None:
        match parsable_url.url_parts:
            case "h", file_dir, _, filename:
                instance = EHentaiImageUrl(parsable_url)
                instance.original_filename = filename
                instance.page = None
                instance.gallery_id = None
                instance.file_hash = file_dir.split("-")[0]
            case _:
                return None

        return instance
