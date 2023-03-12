from danboorutools.logical.extractors.skima import SkimaArtistUrl, SkimaGalleryUrl, SkimaImageUrl, SkimaItemUrl, SkimaUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class SkimaJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> SkimaUrl | None:
        instance: SkimaUrl
        match parsable_url.url_parts:
            # https://skima.jp/gallery?id=37282
            case "gallery", :
                instance = SkimaGalleryUrl(parsable_url)
                instance.gallery_id = int(parsable_url.query["id"].strip("/"))

            # http://skima.jp/item/detail/?item_id=4661/
            case "item", "detail":
                instance = SkimaItemUrl(parsable_url)
                instance.item_id = int(parsable_url.query["item_id"].strip("/"))

            # https://cdn-common.skima.jp/item/180/812/1180812/showcase-ff069e42591011ee6efc95907df64dbe-20230111222024.jpeg
            case "item", *_ if parsable_url.subdomain == "cdn-common":
                instance = SkimaImageUrl(parsable_url)
                instance.post_type = "item"

            # https://cdn-gallery.skima.jp/gallery/529/639/529639/tip-2c639a2be7c4c2984a7d3e894746dcac-20221016015859.jpeg
            # https://cdn-gallery.skima.jp/gallery/529/639/529639/detail-1464a99fb503c40a3282e8d61681657d-20221016015858.jpeg
            # https://cdn-gallery.skima.jp/gallery/529/639/529639/985db8d09a3386f1452ab0eb43e140f5-20221016015858.png
            case "gallery", *_ if parsable_url.subdomain == "cdn-gallery":
                instance = SkimaImageUrl(parsable_url)
                instance.post_type = "gallery"

            # https://skima.jp/profile?id=244678
            case "profile", *_:
                instance = SkimaArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["id"].strip("/"))

            # https://skima.jp/profile/commissions?id=32742
            case "profile", ("commissions" | "galleries" | "dl_products" | "reviews"):
                instance = SkimaArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["id"].strip("/"))

            # http://skima.jp/u/id21469/
            case "u", slug if slug.startswith("id"):
                instance = SkimaArtistUrl(parsable_url)
                instance.user_id = int(slug.removeprefix("id"))

            case _:
                return None

        return instance
