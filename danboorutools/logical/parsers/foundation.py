from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.foundation import FoundationArtistUrl, FoundationImageUrl, FoundationPostUrl, FoundationUrl


class FoundationAppParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FoundationUrl | None:
        instance: FoundationUrl
        if parsable_url.subdomain == "assets":
            match parsable_url.url_parts:
                # https://assets.foundation.app/0x21Afa9aB02B6Fb7cb483ff3667c39eCdd6D9Ea73/4/nft.mp4
                case token_id, work_id, _ if token_id.startswith("0x"):
                    instance = FoundationImageUrl(parsable_url)
                    instance.token_id = token_id
                    instance.work_id = int(work_id)
                    instance.file_hash = None
                # https://assets.foundation.app/7i/gs/QmU8bbsjaVQpEKMDWbSZdDD6GsPmRYBhQtYRn8bEGv7igs/nft_q4.mp4
                case _, _, file_hash, _:
                    instance = FoundationImageUrl(parsable_url)
                    instance.file_hash = file_hash
                    instance.token_id = None
                    instance.work_id = None
                case _:
                    return None
        else:
            match parsable_url.url_parts:
                # https://foundation.app/@mochiiimo/~/97376
                # https://foundation.app/@mochiiimo/foundation/97376
                # https://foundation.app/@KILLERGF/kgfgen/4
                # https://foundation.app/oyariashito/foundation/110329
                case username, collection, post_id:
                    instance = FoundationPostUrl(parsable_url)
                    instance.username = username.removeprefix("@")
                    instance.collection = collection if collection != "~" else "foundation"
                    instance.post_id = int(post_id)

                # https://foundation.app/@asuka111art/dinner-with-cats-82426
                case username, post_slug if "-" in post_slug:
                    instance = FoundationPostUrl(parsable_url)
                    instance.collection = "foundation"
                    instance.post_id = int(post_slug.split("-")[-1])
                    instance.username = username.removeprefix("@")

                # https://foundation.app/@mochiiimo
                # https://foundation.app/@KILLERGF
                case username, if username.startswith("@"):
                    instance = FoundationArtistUrl(parsable_url)
                    instance.username = username[1:]

                # https://foundation.app/0x7E2ef75C0C09b2fc6BCd1C68B6D409720CcD58d2
                case user_hash, if user_hash.startswith("0x"):
                    instance = FoundationArtistUrl(parsable_url)
                    instance.user_hash = user_hash
                    instance.username = None

                case _:
                    return None

        return instance
