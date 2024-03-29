from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.picdig import PicdigArtistImageUrl, PicdigArtistUrl, PicdigImageUrl, PicdigPostUrl, PicdigUrl


class PicdigNetParser(UrlParser):
    RESERVED_NAMES = {"api", "articles", "images", "my", "privacy-policy", "projects", "terms"}

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PicdigUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/54e476f5-f956-497d-b689-0db7e745907d/2021/12/b35f9c35-a37f-47b0-a5b6-e639a4535ce3.jpg
            # https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/54e476f5-f956-497d-b689-0db7e745907d/2021/12/63fffa1f-2862-4aa6-80dc-b5a73d91ab43.png
            case "images", account_id, user_id, _, _, image_id:
                return PicdigImageUrl(parsed_url=parsable_url,
                                      account_id=account_id,
                                      image_id=image_id,
                                      user_id=user_id)

            # https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/2021/12/9fadd3f4-c131-4f26-bce5-26c9d5bd4927.jpg
            case "images", account_id, _, _, image_id:
                return PicdigArtistImageUrl(parsed_url=parsable_url,
                                            account_id=account_id,
                                            image_id=image_id)

            # https://picdig.net/supercanoyan/projects/71c55605-3eca-4660-991c-ee24b9a7b684
            case username, "projects", project_id:
                return PicdigPostUrl(parsed_url=parsable_url,
                                     username=username,
                                     project_id=project_id)

            # https://picdig.net/supercanoyan/portfolio
            # https://picdig.net/supercanoyan/profile
            # https://picdig.net/supercanoyan/collections
            # https://picdig.net/supercanoyan/articles
            case username, *_ if username not in cls.RESERVED_NAMES:
                return PicdigArtistUrl(parsed_url=parsable_url,
                                       username=username)

            case _:
                return None
