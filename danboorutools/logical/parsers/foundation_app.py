from danboorutools.logical.extractors.foundation import FoundationArtistUrl, FoundationImageUrl, FoundationPostUrl, FoundationUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class FoundationAppParser(UrlParser):
    test_cases = {
        FoundationArtistUrl: [
            "https://foundation.app/@mochiiimo",
            "https://foundation.app/@KILLERGF",

            "https://foundation.app/0x7E2ef75C0C09b2fc6BCd1C68B6D409720CcD58d2",
        ],
        FoundationPostUrl: [
            "https://foundation.app/@mochiiimo/~/97376",
            "https://foundation.app/@mochiiimo/foundation/97376",
            "https://foundation.app/@KILLERGF/kgfgen/4",
            "https://foundation.app/@asuka111art/dinner-with-cats-82426",
            "https://foundation.app/oyariashito/foundation/110329",
        ],
        FoundationImageUrl: [
            "https://assets.foundation.app/0x21Afa9aB02B6Fb7cb483ff3667c39eCdd6D9Ea73/4/nft.mp4",
            "https://assets.foundation.app/7i/gs/QmU8bbsjaVQpEKMDWbSZdDD6GsPmRYBhQtYRn8bEGv7igs/nft_q4.mp4",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FoundationUrl | None:
        instance: FoundationUrl
        if parsable_url.subdomain == "assets":
            match parsable_url.url_parts:
                case token_id, work_id, _ if token_id.startswith("0x"):
                    instance = FoundationImageUrl(parsable_url)
                    instance.token_id = token_id
                    instance.work_id = int(work_id)
                    instance.file_hash = None
                case _, _, file_hash, _:
                    instance = FoundationImageUrl(parsable_url)
                    instance.file_hash = file_hash
                    instance.token_id = None
                    instance.work_id = None
                case _:
                    return None
        else:
            match parsable_url.url_parts:
                case artist_name, subdir, post_id:
                    instance = FoundationPostUrl(parsable_url)
                    instance.artist_name = artist_name.removeprefix("@")
                    instance.subdir = subdir
                    instance.post_id = int(post_id)
                case artist_name, post_slug if "-" in post_slug:
                    instance = FoundationPostUrl(parsable_url)
                    instance.subdir = "~"
                    instance.post_id = int(post_slug.split("-")[-1])
                    instance.artist_name = artist_name.removeprefix("@")
                case [artist_name] if artist_name.startswith("@"):
                    instance = FoundationArtistUrl(parsable_url)
                    instance.artist_name = artist_name[1:]
                case [artist_hash] if artist_hash.startswith("0x"):
                    instance = FoundationArtistUrl(parsable_url)
                    instance.artist_hash = artist_hash
                    instance.artist_name = None
                case _:
                    return None

        return instance
