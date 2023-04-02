from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.ehentai import EHentaiGalleryUrl, EHentaiImageUrl, EHentaiPageUrl, EHentaiUrl


class EhentaiOrgParser(UrlParser):

    domains = ["e-hentai.org", "exhentai.org"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EHentaiUrl | None:
        match parsable_url.url_parts:
            # https://e-hentai.org/s/ad41a3fac6/847994-352
            # https://exhentai.org/s/ad41a3fac6/847994-352
            # https://g.e-hentai.org/s/ad41a3fac6/847994-352
            # https://e-hentai.org/s/0251bc4e84/136116-25.jpg
            case "s", page_token, gallery_id_and_page_number, *_:
                try:
                    [gallery_id, page_number] = map(int, gallery_id_and_page_number.split("-"))
                except ValueError:
                    [gallery_id, page_number] = map(int, gallery_id_and_page_number.split(".")[0].split("-"))
                subsite = parsable_url.domain.removesuffix(".org")
                return EHentaiPageUrl(parsed_url=parsable_url,
                                      page_token=page_token[:10],
                                      gallery_id=gallery_id,
                                      page_number=page_number,
                                      subsite=subsite)

            # https://exhentai.org/g/1858690/b62c996bb6/
            # http://g.e-hentai.org/g/1858690/b62c996bb6/
            # http://e-hentai.org/g/1858690/b62c996bb6/
            # http://g.e-hentai.org/g/340478/057192d561/?p=15
            case "g", gallery_id, gallery_token, *_:
                return EHentaiGalleryUrl(parsed_url=parsable_url,
                                         gallery_token=gallery_token,
                                         gallery_id=int(gallery_id),
                                         subsite=parsable_url.domain.removesuffix(".org"))

            # https://exhentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg
            # https://e-hentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg
            case "t", _, _, filename:
                return EHentaiImageUrl(parsed_url=parsable_url,
                                       original_filename=None,
                                       page_token=filename[:10],
                                       file_hash=filename.split("-")[0],
                                       image_type="thumbnail")

            # https://exhentai.org/fullimg.php?gid=2464842&page=2&key=uinj32c9zag
            case "fullimg.php", :
                return EHentaiImageUrl(parsed_url=parsable_url,
                                       original_filename=None,
                                       gallery_id=int(parsable_url.query["gid"]),
                                       page_number=int(parsable_url.query["page"]),
                                       file_hash=None,
                                       image_type="download")

            # https://g.e-hentai.org/?f_shash=85f4d25b291210a2a6936331a1e7202741392715\u0026fs_from=_039.jpg
            case []:
                if not parsable_url.query:
                    raise UnparsableUrlError(parsable_url)
                return EHentaiImageUrl(parsed_url=parsable_url,
                                       file_hash=parsable_url.query["f_shash"],
                                       page_token=parsable_url.query["f_shash"][:10],
                                       original_filename=parsable_url.query["fs_from"],
                                       image_type="hash_link")

            case _:
                if parsable_url.raw_url == "https://exhentai.org/img/kokomade.jpg":
                    raise UnparsableUrlError(parsable_url)
                # https://repo.e-hentai.org/bounty/fc/fcf12a1928e4d3b49bebe5280238e00de52027de-455288.jpg-thumb.jpg
                elif parsable_url.subdomain in ["repo", "forums"]:
                    raise UnparsableUrlError(parsable_url)
                # http://g.e-hentai.org/tag/artist%3Ayatsuki
                elif parsable_url.url_parts[0] in ["tag"]:
                    raise UnparsableUrlError(parsable_url)
                else:
                    return None


class EhgtOrgParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EHentaiImageUrl | None:
        match parsable_url.url_parts:
            # http://gt2.ehgt.org/a8/9a/a89a1ecc242a1f64edc56bf253442f46e937cdf3-578970-1000-1000-jpg_m.jpg,
            case _, _, filename:
                return EHentaiImageUrl(parsed_url=parsable_url,
                                       original_filename=None,
                                       file_hash=filename.split("-")[0],
                                       page_token=filename[:10],
                                       image_type="direct")

            case _:
                return None


class HathNetworkParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EHentaiImageUrl | None:
        match parsable_url.url_parts:
            # https://ijmwujr.grduyvrrtxiu.hath.network:40162/h/5bf1c8b26c4d0d35951b7116d151209f6784420e-137816-810-1228-jpg/keystamp=1676307900-1fa0db7a58;fileindex=120969163;xres=2400/4134835_103198602_p0.jpg
            case "h", file_dir, _, filename:
                return EHentaiImageUrl(parsed_url=parsable_url,
                                       original_filename=filename,
                                       file_hash=file_dir.split("-")[0],
                                       image_type="direct")

            case _:
                return None
