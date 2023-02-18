from danboorutools.logical.extractors.ehentai import EHentaiImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class EhgtOrgParser(UrlParser):
    test_cases = {
        EHentaiImageUrl: [
            "http://gt2.ehgt.org/a8/9a/a89a1ecc242a1f64edc56bf253442f46e937cdf3-578970-1000-1000-jpg_m.jpg",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EHentaiImageUrl | None:
        match parsable_url.url_parts:
            case _, _, filename:
                instance = EHentaiImageUrl(parsable_url)
                instance.original_filename = None
                instance.file_hash = filename.split("-")[0]
                instance.page_token = filename[:10]
                instance.image_type = "direct"
            case _:
                return None
        return instance
