from danboorutools.logical.extractors.arca_live import ArcaLiveImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NamuLaParser(UrlParser):
    test_cases = {
        ArcaLiveImageUrl: [
            "https://ac2.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg",
            "https://ac2.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig",
            "https://ac2-o.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig",
            "https://ac.namu.la/20221211sac/5ea7fbca5e49ec16beb099fc6fc991690d37552e599b1de8462533908346241e.png",
            "https://ac-o.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.gif?type=orig",
            "https://ac.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.mp4",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ArcaLiveImageUrl | None:
        match parsable_url.url_parts:
            case date_string, filename:
                instance = ArcaLiveImageUrl(parsable_url)
                instance.date_string = date_string
                instance.filename = filename
            case _:
                return None
        return instance
