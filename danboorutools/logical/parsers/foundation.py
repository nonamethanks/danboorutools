from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.foundation import FoundationArtistUrl, FoundationImageUrl, FoundationPostUrl, FoundationUrl


class FoundationAppParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FoundationUrl | None:
        if parsable_url.subdomain == "assets":
            return cls._match_asset(parsable_url)
        else:
            return cls._match_everything_else(parsable_url)

    @staticmethod
    def _match_asset(parsable_url: ParsableUrl) -> FoundationImageUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://assets.foundation.app/0x21Afa9aB02B6Fb7cb483ff3667c39eCdd6D9Ea73/4/nft.mp4
            case token_id, work_id, _ if token_id.startswith("0x"):
                return FoundationImageUrl(parsed_url=parsable_url,
                                          token_id=token_id,
                                          file_hash=None,
                                          work_id=int(work_id))

            # https://assets.foundation.app/7i/gs/QmU8bbsjaVQpEKMDWbSZdDD6GsPmRYBhQtYRn8bEGv7igs/nft_q4.mp4
            case _, _, file_hash, _:
                return FoundationImageUrl(parsed_url=parsable_url,
                                          file_hash=file_hash,
                                          work_id=None,
                                          token_id=None)

            case _:
                return None

    @staticmethod
    def _match_everything_else(parsable_url: ParsableUrl) -> FoundationUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://foundation.app/@mochiiimo/~/97376
            # https://foundation.app/@mochiiimo/foundation/97376
            # https://foundation.app/@KILLERGF/kgfgen/4
            # https://foundation.app/oyariashito/foundation/110329
            case username, collection, post_id:
                return FoundationPostUrl(parsed_url=parsable_url,
                                         username=username.removeprefix("@"),
                                         post_id=int(post_id),
                                         collection=collection if collection != "~" else "foundation")

            # https://foundation.app/@asuka111art/dinner-with-cats-82426
            case username, post_slug if "-" in post_slug:
                return FoundationPostUrl(parsed_url=parsable_url,
                                         collection="foundation",
                                         username=username.removeprefix("@"),
                                         post_id=int(post_slug.split("-")[-1]))

            # https://foundation.app/@mochiiimo
            # https://foundation.app/@KILLERGF
            case username, if username.startswith("@"):
                return FoundationArtistUrl(parsed_url=parsable_url,
                                           username=username[1:])

            # https://foundation.app/0x7E2ef75C0C09b2fc6BCd1C68B6D409720CcD58d2
            case user_hash, if user_hash.startswith("0x"):
                return FoundationArtistUrl(parsed_url=parsable_url,
                                           user_hash=user_hash,
                                           username=None)

            case _:
                return None
