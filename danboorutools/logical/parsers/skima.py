from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.skima import SkimaArtistUrl, SkimaGalleryUrl, SkimaImageUrl, SkimaItemUrl, SkimaUrl


class SkimaJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> SkimaUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://skima.jp/gallery?id=37282
            case "gallery", :
                return SkimaGalleryUrl(parsed_url=parsable_url,
                                       gallery_id=int(parsable_url.query["id"].strip("/")))

            # http://skima.jp/item/detail/?item_id=4661/
            case "item", "detail":
                return SkimaItemUrl(parsed_url=parsable_url,
                                    item_id=int(parsable_url.query["item_id"].strip("/")))

            # https://cdn-common.skima.jp/item/180/812/1180812/showcase-ff069e42591011ee6efc95907df64dbe-20230111222024.jpeg
            case "item", *_ if parsable_url.subdomain == "cdn-common":
                return SkimaImageUrl(parsed_url=parsable_url,
                                     post_type="item")

            # https://cdn-gallery.skima.jp/gallery/529/639/529639/tip-2c639a2be7c4c2984a7d3e894746dcac-20221016015859.jpeg
            # https://cdn-gallery.skima.jp/gallery/529/639/529639/detail-1464a99fb503c40a3282e8d61681657d-20221016015858.jpeg
            # https://cdn-gallery.skima.jp/gallery/529/639/529639/985db8d09a3386f1452ab0eb43e140f5-20221016015858.png
            case "gallery", *_ if parsable_url.subdomain == "cdn-gallery":
                return SkimaImageUrl(parsed_url=parsable_url,
                                     post_type="gallery")

            # https://skima.jp/profile?id=244678
            case "profile", *_:
                return SkimaArtistUrl(parsed_url=parsable_url,
                                      user_id=int(parsable_url.query["id"].strip("/")))

            # https://skima.jp/profile/commissions?id=32742
            case "profile", ("commissions" | "galleries" | "dl_products" | "reviews"):
                return SkimaArtistUrl(parsed_url=parsable_url,
                                      user_id=int(parsable_url.query["id"].strip("/")))

            # http://skima.jp/u/id21469/
            case "u", slug if slug.startswith("id"):
                return SkimaArtistUrl(parsed_url=parsable_url,
                                      user_id=int(slug.removeprefix("id")))

            # https://skima.jp/u/id13356/まで
            case "u", slug, _ if slug.startswith("id"):
                return SkimaArtistUrl(parsed_url=parsable_url,
                                      user_id=int(slug.removeprefix("id")))

            case _:
                return None
