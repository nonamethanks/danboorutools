
from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.anifty import AniftyImageUrl
from danboorutools.logical.extractors.foundation import FoundationImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class ImgixNetParser(UrlParser):
    test_cases = {
        AniftyImageUrl: [
            "https://anifty.imgix.net/creation/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/20d5ce5b5163a71258e1d0ee152a0347bf40c7da.png?w=660&h=660&fit=crop&crop=focalpoint&fp-x=0.76&fp-y=0.5&fp-z=1&auto=compress",
            "https://anifty.imgix.net/creation/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/48b1409838cf7271413480b8533372844b9f2437.png?w=3840&q=undefined&auto=compress",
        ],
        FoundationImageUrl: [
            "https://f8n-ipfs-production.imgix.net/QmX4MotNAAj9Rcyew43KdgGDxU1QtXemMHoUTNacMLLSjQ/nft.png",
            "https://f8n-ipfs-production.imgix.net/QmX4MotNAAj9Rcyew43KdgGDxU1QtXemMHoUTNacMLLSjQ/nft.png?q=80&auto=format%2Ccompress&cs=srgb&max-w=1680&max-h=1680",
            "https://f8n-production-collection-assets.imgix.net/0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405/128711/QmcBfbeCMSxqYB3L1owPAxFencFx3jLzCPFx6xUBxgSCkH/nft.png",
            "https://f8n-production-collection-assets.imgix.net/0x18e7E64a51bF26e9DcC167C28a52E4c85781d52E/17/nft.png",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AniftyImageUrl | FoundationImageUrl | None:
        if parsable_url.subdomain == "anifty":
            return cls._match_anifty(parsable_url)
        elif parsable_url.subdomain in ("f8n-ipfs-production", "f8n-production-collection-assets"):
            return cls._match_foundation(parsable_url)
        else:
            raise UnparsableUrl(parsable_url)

    @staticmethod
    def _match_anifty(parsable_url: ParsableUrl) -> AniftyImageUrl | None:
        match parsable_url.url_parts:
            case _, artist_hash, _ if artist_hash.startswith("0x"):
                instance = AniftyImageUrl(parsable_url)
                instance.artist_hash = artist_hash
            case _:
                return None

        return instance

    @staticmethod
    def _match_foundation(parsable_url: ParsableUrl) -> FoundationImageUrl | None:
        match parsable_url.url_parts:
            case token_id, work_id, file_hash, _ if token_id.startswith("0x"):
                instance = FoundationImageUrl(parsable_url)
                instance.token_id = token_id
                instance.work_id = int(work_id)
                instance.file_hash = file_hash
            case token_id, work_id, _ if token_id.startswith("0x"):
                instance = FoundationImageUrl(parsable_url)
                instance.token_id = token_id
                instance.work_id = int(work_id)
                instance.file_hash = None
            case file_hash, _:
                instance = FoundationImageUrl(parsable_url)
                instance.file_hash = file_hash
                instance.token_id = None
                instance.work_id = None
            case _:
                return None

        return instance
