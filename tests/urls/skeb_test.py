import pytest

from danboorutools.logical.urls.skeb import SkebAbsolutePostUrl, SkebArtistUrl, SkebImageUrl, SkebPostUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    SkebArtistUrl: {
        "https://skeb.jp/OrvMZ": "https://skeb.jp/@OrvMZ",
        "https://skeb.jp/@asanagi": "https://skeb.jp/@asanagi",
        "https://skeb.jp/@okku_oxn/works": "https://skeb.jp/@okku_oxn",

    },
    SkebPostUrl: {
        "https://skeb.jp/@OrvMZ/works/3": "https://skeb.jp/@OrvMZ/works/3",
        "https://skeb.jp/@OrvMZ/works/1": "https://skeb.jp/@OrvMZ/works/1",
        "https://skeb.jp/@asanagi/works/16": "https://skeb.jp/@asanagi/works/16",
        "https://skeb.jp/@asanagi/works/6": "https://skeb.jp/@asanagi/works/6",
        "https://skeb.jp/@nasuno42/works/30": "https://skeb.jp/@nasuno42/works/30",
    },
    SkebAbsolutePostUrl: {
        "https://skeb.jp/works/713654": "https://skeb.jp/works/713654",
    },
    SkebImageUrl: {
        "https://skeb.imgix.net/requests/199886_0?bg=%23fff&auto=format&w=800&s=5a6a908ab964fcdfc4713fad179fe715": "https://skeb.imgix.net/requests/199886_0?bg=%23fff&auto=format&w=800&s=5a6a908ab964fcdfc4713fad179fe715",
        "https://skeb.imgix.net/requests/73290_0?bg=%23fff&auto=format&txtfont=bold&txtshad=70&txtclr=BFFFFFFF&txtalign=middle%2Ccenter&txtsize=150&txt=SAMPLE&w=800&s=4843435cff85d623b1f657209d131526": "https://skeb.imgix.net/requests/73290_0?bg=%23fff&auto=format&txtfont=bold&txtshad=70&txtclr=BFFFFFFF&txtalign=middle%2Ccenter&txtsize=150&txt=SAMPLE&w=800&s=4843435cff85d623b1f657209d131526",
        "https://skeb.imgix.net/requests/53269_1?bg=%23fff&fm=png&dl=53269.png&w=1.0&h=1.0&s=44588ea9c41881049e392adb1df21cce": "https://skeb.imgix.net/requests/53269_1?bg=%23fff&fm=png&dl=53269.png&w=1.0&h=1.0&s=44588ea9c41881049e392adb1df21cce",
        "https://skeb.imgix.net/uploads/origins/04d62c2f-e396-46f9-903a-3ca8bd69fc7c?bg=%23fff&auto=format&w=800&s=966c5d0389c3b94dc36ac970f812bef4": "https://skeb.imgix.net/uploads/origins/04d62c2f-e396-46f9-903a-3ca8bd69fc7c?bg=%23fff&auto=format&w=800&s=966c5d0389c3b94dc36ac970f812bef4",
        "https://fcdn.skeb.jp/uploads/outputs/20f9d68f-50ec-44ae-8630-173fc38a2d6a?response-content-disposition=inline&Expires=1676373664&Signature=BNFCR248Xkvk4E8Th-a1~zopTL1NvP9rhu78n7YSSPt9K2PGM5GgmLLiXltj~5FteosdONepKLVeENVxTFBXRj~FgOGYQV7AehfBF2eMYB6V3v9at1cxFsqOFXjiPHohmqRzvzKHlVe-GlA6U4~ClYKsw0Ur9QSIlZ79iJlsTIbz~wzIzp463h~8KuAi81oBSLvdOJkm1qpEY2Em0PjUtNfx36Gk5jjCPRq5oVvITkdc~VrLLR~GNPjWAedkEhct~aVMAU56PQH6Few0LNoqjmCJZeY2d8mz0lugICGq2S9JPMmPQVR7HOFD0x3JBpX3-WWSmhC3F8f8lkErVNAv~A__&Key-Pair-Id=K1GS3H53SEO647": "https://fcdn.skeb.jp/uploads/outputs/20f9d68f-50ec-44ae-8630-173fc38a2d6a?response-content-disposition=inline&Expires=1676373664&Signature=BNFCR248Xkvk4E8Th-a1~zopTL1NvP9rhu78n7YSSPt9K2PGM5GgmLLiXltj~5FteosdONepKLVeENVxTFBXRj~FgOGYQV7AehfBF2eMYB6V3v9at1cxFsqOFXjiPHohmqRzvzKHlVe-GlA6U4~ClYKsw0Ur9QSIlZ79iJlsTIbz~wzIzp463h~8KuAi81oBSLvdOJkm1qpEY2Em0PjUtNfx36Gk5jjCPRq5oVvITkdc~VrLLR~GNPjWAedkEhct~aVMAU56PQH6Few0LNoqjmCJZeY2d8mz0lugICGq2S9JPMmPQVR7HOFD0x3JBpX3-WWSmhC3F8f8lkErVNAv~A__&Key-Pair-Id=K1GS3H53SEO647",
        "https://cdn.skeb.jp/uploads/outputs/20f9d68f-50ec-44ae-8630-173fc38a2d6a?response-content-disposition=inline&Expires=1676373664&Signature=BNFCR248Xkvk4E8Th-a1~zopTL1NvP9rhu78n7YSSPt9K2PGM5GgmLLiXltj~5FteosdONepKLVeENVxTFBXRj~FgOGYQV7AehfBF2eMYB6V3v9at1cxFsqOFXjiPHohmqRzvzKHlVe-GlA6U4~ClYKsw0Ur9QSIlZ79iJlsTIbz~wzIzp463h~8KuAi81oBSLvdOJkm1qpEY2Em0PjUtNfx36Gk5jjCPRq5oVvITkdc~VrLLR~GNPjWAedkEhct~aVMAU56PQH6Few0LNoqjmCJZeY2d8mz0lugICGq2S9JPMmPQVR7HOFD0x3JBpX3-WWSmhC3F8f8lkErVNAv~A__&Key-Pair-Id=K1GS3H53SEO647": "https://cdn.skeb.jp/uploads/outputs/20f9d68f-50ec-44ae-8630-173fc38a2d6a?response-content-disposition=inline&Expires=1676373664&Signature=BNFCR248Xkvk4E8Th-a1~zopTL1NvP9rhu78n7YSSPt9K2PGM5GgmLLiXltj~5FteosdONepKLVeENVxTFBXRj~FgOGYQV7AehfBF2eMYB6V3v9at1cxFsqOFXjiPHohmqRzvzKHlVe-GlA6U4~ClYKsw0Ur9QSIlZ79iJlsTIbz~wzIzp463h~8KuAi81oBSLvdOJkm1qpEY2Em0PjUtNfx36Gk5jjCPRq5oVvITkdc~VrLLR~GNPjWAedkEhct~aVMAU56PQH6Few0LNoqjmCJZeY2d8mz0lugICGq2S9JPMmPQVR7HOFD0x3JBpX3-WWSmhC3F8f8lkErVNAv~A__&Key-Pair-Id=K1GS3H53SEO647",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
