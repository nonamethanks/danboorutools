
from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.anifty import AniftyImageUrl
from danboorutools.logical.extractors.foundation import FoundationImageUrl
from danboorutools.logical.extractors.skeb import SkebImageUrl
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
        ],
        SkebImageUrl: [
            "https://skeb.imgix.net/requests/199886_0?bg=%23fff&auto=format&w=800&s=5a6a908ab964fcdfc4713fad179fe715",
            "https://skeb.imgix.net/requests/73290_0?bg=%23fff&auto=format&txtfont=bold&txtshad=70&txtclr=BFFFFFFF&txtalign=middle%2Ccenter&txtsize=150&txt=SAMPLE&w=800&s=4843435cff85d623b1f657209d131526",
            "https://skeb.imgix.net/requests/53269_1?bg=%23fff&fm=png&dl=53269.png&w=1.0&h=1.0&s=44588ea9c41881049e392adb1df21cce",
            "https://skeb.imgix.net/uploads/origins/04d62c2f-e396-46f9-903a-3ca8bd69fc7c?bg=%23fff&auto=format&w=800&s=966c5d0389c3b94dc36ac970f812bef4",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AniftyImageUrl | FoundationImageUrl | SkebImageUrl | None:
        if parsable_url.subdomain == "anifty":
            return cls._match_anifty(parsable_url)
        elif parsable_url.subdomain in ("f8n-ipfs-production", "f8n-production-collection-assets"):
            return cls._match_foundation(parsable_url)
        elif parsable_url.subdomain == "skeb":
            return cls._match_skeb(parsable_url)
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

    @staticmethod
    def _match_skeb(parsable_url: ParsableUrl) -> SkebImageUrl | None:
        match parsable_url.url_parts:
            case "requests", filename:
                instance = SkebImageUrl(parsable_url)
                [instance.post_id, instance.page] = map(int, filename.split("_"))
                instance.image_uuid = None

            case "uploads", "origins", image_uuid:
                instance = SkebImageUrl(parsable_url)
                instance.image_uuid = image_uuid
                instance.page = None
                instance.post_id = None

            case _:
                return None

        return instance
