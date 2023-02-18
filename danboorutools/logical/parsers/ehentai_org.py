from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.ehentai import EHentaiGalleryUrl, EHentaiImageUrl, EHentaiPageUrl, EHentaiUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class EhentaiOrgParser(UrlParser):
    test_cases = {
        EHentaiGalleryUrl: [
            "https://exhentai.org/g/1858690/b62c996bb6/",
            "http://g.e-hentai.org/g/1858690/b62c996bb6/",
            "http://e-hentai.org/g/1858690/b62c996bb6/",
            "http://g.e-hentai.org/g/340478/057192d561/?p=15",
        ],
        EHentaiImageUrl: [
            "https://exhentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg",
            "https://e-hentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg",
            "https://g.e-hentai.org/?f_shash=85f4d25b291210a2a6936331a1e7202741392715\u0026fs_from=_039.jpg",
            "https://exhentai.org/fullimg.php?gid=2464842&page=2&key=uinj32c9zag",
        ],
        EHentaiPageUrl: [
            "https://e-hentai.org/s/ad41a3fac6/847994-352",
            "https://exhentai.org/s/ad41a3fac6/847994-352",
            "https://g.e-hentai.org/s/ad41a3fac6/847994-352",
            "https://e-hentai.org/s/0251bc4e84/136116-25.jpg",
        ],
    }

    domains = ["e-hentai.org", "exhentai.org"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EHentaiUrl | None:
        instance: EHentaiUrl

        match parsable_url.url_parts:
            # https://e-hentai.org/s/ad41a3fac6/847994-352
            # https://exhentai.org/s/ad41a3fac6/847994-352
            # https://g.e-hentai.org/s/ad41a3fac6/847994-352
            # https://e-hentai.org/s/0251bc4e84/136116-25.jpg
            case "s", page_token, gallery_id_and_page_number, *_:
                instance = EHentaiPageUrl(parsable_url)
                instance.page_token = page_token[:10]
                try:
                    [instance.gallery_id, instance.page_number] = map(int, gallery_id_and_page_number.split("-"))
                except ValueError:
                    [instance.gallery_id, instance.page_number] = map(int, gallery_id_and_page_number.split(".")[0].split("-"))
                instance.subsite = parsable_url.domain.removesuffix(".org")

            # https://exhentai.org/g/1858690/b62c996bb6/
            # http://g.e-hentai.org/g/1858690/b62c996bb6/
            # http://e-hentai.org/g/1858690/b62c996bb6/
            # http://g.e-hentai.org/g/340478/057192d561/?p=15
            case "g", gallery_id, gallery_token, *_:
                instance = EHentaiGalleryUrl(parsable_url)
                instance.gallery_token = gallery_token
                instance.gallery_id = int(gallery_id)
                instance.subsite = parsable_url.domain.removesuffix(".org")

            # https://exhentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg
            # https://e-hentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg
            case "t", _, _, filename:
                instance = EHentaiImageUrl(parsable_url)
                instance.original_filename = None
                instance.page_token = filename[:10]
                instance.file_hash = filename.split("-")[0]
                instance.image_type = "thumbnail"

            # https://exhentai.org/fullimg.php?gid=2464842&page=2&key=uinj32c9zag
            case ["fullimg.php"]:
                instance = EHentaiImageUrl(parsable_url)
                instance.original_filename = None
                instance.gallery_id = int(parsable_url.params["gid"])
                instance.page_number = int(parsable_url.params["page"])
                instance.file_hash = None
                instance.image_type = "download"

            # https://g.e-hentai.org/?f_shash=85f4d25b291210a2a6936331a1e7202741392715\u0026fs_from=_039.jpg
            case []:
                if not parsable_url.params:
                    raise UnparsableUrl(parsable_url)
                instance = EHentaiImageUrl(parsable_url)
                instance.file_hash = parsable_url.params["f_shash"]
                instance.page_token = instance.file_hash[:10]
                instance.original_filename = parsable_url.params["fs_from"]
                instance.image_type = "hash_link"

            case _:
                if parsable_url.url == "https://exhentai.org/img/kokomade.jpg":
                    raise UnparsableUrl(parsable_url)
                # https://repo.e-hentai.org/bounty/fc/fcf12a1928e4d3b49bebe5280238e00de52027de-455288.jpg-thumb.jpg
                elif parsable_url.subdomain in ["repo", "forums"]:
                    raise UnparsableUrl(parsable_url)
                # http://g.e-hentai.org/tag/artist%3Ayatsuki
                elif parsable_url.url_parts[0] in ["tag"]:
                    raise UnparsableUrl(parsable_url)
                else:
                    return None

        return instance
