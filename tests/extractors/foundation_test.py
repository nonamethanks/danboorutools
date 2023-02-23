from ward import test

from danboorutools.models.url import Url

urls = {
    "https://foundation.app/@mochiiimo": "https://foundation.app/@mochiiimo",
    "https://foundation.app/@KILLERGF": "https://foundation.app/@KILLERGF",

    "https://foundation.app/0x7E2ef75C0C09b2fc6BCd1C68B6D409720CcD58d2": "https://foundation.app/0x7E2ef75C0C09b2fc6BCd1C68B6D409720CcD58d2",
    "https://foundation.app/@mochiiimo/~/97376": "https://foundation.app/@mochiiimo/foundation/97376",
    "https://foundation.app/@mochiiimo/foundation/97376": "https://foundation.app/@mochiiimo/foundation/97376",
    "https://foundation.app/@KILLERGF/kgfgen/4": "https://foundation.app/@KILLERGF/kgfgen/4",
    "https://foundation.app/@asuka111art/dinner-with-cats-82426": "https://foundation.app/@asuka111art/foundation/82426",
    "https://foundation.app/oyariashito/foundation/110329": "https://foundation.app/@oyariashito/foundation/110329",

    "https://assets.foundation.app/0x21Afa9aB02B6Fb7cb483ff3667c39eCdd6D9Ea73/4/nft.mp4": "https://assets.foundation.app/0x21Afa9aB02B6Fb7cb483ff3667c39eCdd6D9Ea73/4/nft.mp4",
    "https://assets.foundation.app/7i/gs/QmU8bbsjaVQpEKMDWbSZdDD6GsPmRYBhQtYRn8bEGv7igs/nft_q4.mp4": "https://f8n-ipfs-production.imgix.net/QmU8bbsjaVQpEKMDWbSZdDD6GsPmRYBhQtYRn8bEGv7igs/nft.mp4",

    "https://d2ybmb80bbm9ts.cloudfront.net/zd/BD/QmXiCEoBLcpfvpEwAEanLXe3Tjr5ykYJFzCVfpzDDQzdBD/nft_q4.mp4": "https://f8n-ipfs-production.imgix.net/QmXiCEoBLcpfvpEwAEanLXe3Tjr5ykYJFzCVfpzDDQzdBD/nft.mp4",

    "https://f8n-ipfs-production.imgix.net/QmX4MotNAAj9Rcyew43KdgGDxU1QtXemMHoUTNacMLLSjQ/nft.png": "https://f8n-ipfs-production.imgix.net/QmX4MotNAAj9Rcyew43KdgGDxU1QtXemMHoUTNacMLLSjQ/nft.png",
    "https://f8n-ipfs-production.imgix.net/QmX4MotNAAj9Rcyew43KdgGDxU1QtXemMHoUTNacMLLSjQ/nft.png?q=80&auto=format%2Ccompress&cs=srgb&max-w=1680&max-h=1680": "https://f8n-ipfs-production.imgix.net/QmX4MotNAAj9Rcyew43KdgGDxU1QtXemMHoUTNacMLLSjQ/nft.png",
    "https://f8n-production-collection-assets.imgix.net/0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405/128711/QmcBfbeCMSxqYB3L1owPAxFencFx3jLzCPFx6xUBxgSCkH/nft.png": "https://f8n-ipfs-production.imgix.net/QmcBfbeCMSxqYB3L1owPAxFencFx3jLzCPFx6xUBxgSCkH/nft.png",
    "https://f8n-production-collection-assets.imgix.net/0x18e7E64a51bF26e9DcC167C28a52E4c85781d52E/17/nft.png": "https://f8n-production-collection-assets.imgix.net/0x18e7E64a51bF26e9DcC167C28a52E4c85781d52E/17/nft.png",
}

for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
