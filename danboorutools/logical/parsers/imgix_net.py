from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.anifty import AniftyImageUrl
from danboorutools.logical.urls.foundation import FoundationImageUrl
from danboorutools.logical.urls.skeb import SkebImageUrl


class ImgixNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AniftyImageUrl | FoundationImageUrl | SkebImageUrl | None:
        if parsable_url.subdomain == "anifty":
            return cls._match_anifty(parsable_url)
        elif parsable_url.subdomain in ("f8n-ipfs-production", "f8n-production-collection-assets"):
            return cls._match_foundation(parsable_url)
        elif parsable_url.subdomain in ("skeb", "si"):
            return cls._match_skeb(parsable_url)
        else:
            raise UnparsableUrlError(parsable_url)

    @staticmethod
    def _match_anifty(parsable_url: ParsableUrl) -> AniftyImageUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case _, artist_hash, filename if artist_hash.startswith("0x"):
                return AniftyImageUrl(parsed_url=parsable_url,
                                      artist_hash=artist_hash,
                                      filename=filename)

            case _:
                return None

    @staticmethod
    def _match_foundation(parsable_url: ParsableUrl) -> FoundationImageUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case token_id, work_id, file_hash, _ if token_id.startswith("0x"):
                return FoundationImageUrl(parsed_url=parsable_url,
                                          token_id=token_id,
                                          file_hash=file_hash,
                                          work_id=int(work_id))
            case token_id, work_id, _ if token_id.startswith("0x"):
                return FoundationImageUrl(parsed_url=parsable_url,
                                          token_id=token_id,
                                          file_hash=None,
                                          work_id=int(work_id))

            case file_hash, _:
                return FoundationImageUrl(parsed_url=parsable_url,
                                          file_hash=file_hash,
                                          work_id=None,
                                          token_id=None)

            case _:
                return None

    @staticmethod
    def _match_skeb(parsable_url: ParsableUrl) -> SkebImageUrl | None:
        match parsable_url.url_parts:
            case "requests", filename:
                [post_id, page] = map(int, filename.split("_"))
                return SkebImageUrl(parsed_url=parsable_url,
                                    post_id=post_id,
                                    page=page,
                                    image_uuid=None)

            case *_, "uploads", "origins", image_uuid:
                return SkebImageUrl(parsed_url=parsable_url,
                                    image_uuid=image_uuid,
                                    post_id=None,
                                    page=None)

            case _:
                return None
