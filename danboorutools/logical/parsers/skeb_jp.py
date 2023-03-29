from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.skeb import SkebAbsolutePostUrl, SkebArtistUrl, SkebImageUrl, SkebPostUrl, SkebUrl


class SkebJpParser(UrlParser):
    RESERVED_USERNAMES = ["works", "users", "about", "terms", "creator", "client", "company"]

    test_cases = {
        SkebArtistUrl: [
            "https://skeb.jp/OrvMZ",
            "https://skeb.jp/@asanagi",
            "https://skeb.jp/@okku_oxn/works",
        ],
        SkebImageUrl: [
            "https://fcdn.skeb.jp/uploads/outputs/20f9d68f-50ec-44ae-8630-173fc38a2d6a?response-content-disposition=inline&Expires=1676373664&Signature=BNFCR248Xkvk4E8Th-a1~zopTL1NvP9rhu78n7YSSPt9K2PGM5GgmLLiXltj~5FteosdONepKLVeENVxTFBXRj~FgOGYQV7AehfBF2eMYB6V3v9at1cxFsqOFXjiPHohmqRzvzKHlVe-GlA6U4~ClYKsw0Ur9QSIlZ79iJlsTIbz~wzIzp463h~8KuAi81oBSLvdOJkm1qpEY2Em0PjUtNfx36Gk5jjCPRq5oVvITkdc~VrLLR~GNPjWAedkEhct~aVMAU56PQH6Few0LNoqjmCJZeY2d8mz0lugICGq2S9JPMmPQVR7HOFD0x3JBpX3-WWSmhC3F8f8lkErVNAv~A__&Key-Pair-Id=K1GS3H53SEO647",
            "https://cdn.skeb.jp/uploads/outputs/20f9d68f-50ec-44ae-8630-173fc38a2d6a?response-content-disposition=inline&Expires=1676373664&Signature=BNFCR248Xkvk4E8Th-a1~zopTL1NvP9rhu78n7YSSPt9K2PGM5GgmLLiXltj~5FteosdONepKLVeENVxTFBXRj~FgOGYQV7AehfBF2eMYB6V3v9at1cxFsqOFXjiPHohmqRzvzKHlVe-GlA6U4~ClYKsw0Ur9QSIlZ79iJlsTIbz~wzIzp463h~8KuAi81oBSLvdOJkm1qpEY2Em0PjUtNfx36Gk5jjCPRq5oVvITkdc~VrLLR~GNPjWAedkEhct~aVMAU56PQH6Few0LNoqjmCJZeY2d8mz0lugICGq2S9JPMmPQVR7HOFD0x3JBpX3-WWSmhC3F8f8lkErVNAv~A__&Key-Pair-Id=K1GS3H53SEO647",

        ],
        SkebPostUrl: [
            "https://skeb.jp/@OrvMZ/works/3",
            "https://skeb.jp/@OrvMZ/works/1",
            "https://skeb.jp/@asanagi/works/16",
            "https://skeb.jp/@asanagi/works/6",
            "https://skeb.jp/@nasuno42/works/30",
        ],
        SkebAbsolutePostUrl: [
            "https://skeb.jp/works/713654",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> SkebUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case username, "works", post_id:
                return SkebPostUrl(parsed_url=parsable_url,
                                   post_id=int(post_id),
                                   username=username.removeprefix("@"))

            case "uploads", "outputs", image_uuid:
                return SkebImageUrl(parsed_url=parsable_url,
                                    image_uuid=image_uuid,
                                    page=None,
                                    post_id=None)

            case "works", post_id:
                return SkebAbsolutePostUrl(parsed_url=parsable_url,
                                           absolute_post_id=int(post_id))

            case username, *_ if username not in cls.RESERVED_USERNAMES:
                return SkebArtistUrl(parsed_url=parsable_url,
                                     username=username.removeprefix("@"))

            case _:
                return None
