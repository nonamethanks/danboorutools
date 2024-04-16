import re

from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.tumblr import TumblrArtistUrl, TumblrImageUrl, TumblrPostUrl, TumblrStaticImageUrl, TumblrUrl


class TumblrComParser(UrlParser):
    RESERVED_NAMES = {"about", "app", "blog", "dashboard", "developers", "explore", "jobs",
                      "login", "logo", "policy", "press", "register", "security", "tagged", "tips"}

    dimensions_pattern = re.compile(fr"^{TumblrImageUrl.dimensions_pattern.pattern}$")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TumblrUrl | None:
        if parsable_url.hostname.endswith(".media.tumblr.com") or parsable_url.hostname in ["data.tumblr.com", "media.tumblr.com"]:
            return cls._match_images(parsable_url)
        elif parsable_url.subdomain in ["www", ""]:
            return cls._match_no_subdomain(parsable_url)
        elif parsable_url.subdomain == "at":
            return cls._match_at_subdomain(parsable_url)
        elif parsable_url.subdomain in ["static"]:
            return cls._match_static(parsable_url)
        else:
            return cls._match_with_subdomain(parsable_url)

    @classmethod
    def _match_images(cls, parsable_url: ParsableUrl) -> TumblrUrl | None:
        match parsable_url.url_parts:

            # https://66.media.tumblr.com/168dabd09d5ad69eb5fedcf94c45c31a/3dbfaec9b9e0c2e3-72/s640x960/bf33a1324f3f36d2dc64f011bfeab4867da62bc8.png
            # https://66.media.tumblr.com/5a2c3fe25c977e2281392752ab971c90/3dbfaec9b9e0c2e3-92/s500x750/4f92bbaaf95c0b4e7970e62b1d2e1415859dd659.png
            # https://64.media.tumblr.com/69d9610907a11c401a1fb1082afc5c58/1ff28e90379f022e-78/s75x75_c1/a6e19624f4194d59f453b7e9d75b3ed5a3e441a1.jpg
            case *_, dimensions, _ if cls.dimensions_pattern.match(dimensions):
                return TumblrImageUrl(parsed_url=parsable_url)

            # http://data.tumblr.com/07e7bba538046b2b586433976290ee1f/tumblr_o3gg44HcOg1r9pi29o1_raw.jpg
            # https://40.media.tumblr.com/de018501416a465d898d24ad81d76358/tumblr_nfxt7voWDX1rsd4umo1_r23_1280.jpg
            # https://media.tumblr.com/de018501416a465d898d24ad81d76358/tumblr_nfxt7voWDX1rsd4umo1_r23_raw.jpg
            # https://66.media.tumblr.com/2c6f55531618b4335c67e29157f5c1fc/tumblr_pz4a44xdVj1ssucdno1_1280.png
            # https://68.media.tumblr.com/ee02048f5578595badc95905e17154b4/tumblr_inline_ofbr4452601sk4jd9_250.gif
            # https://media.tumblr.com/ee02048f5578595badc95905e17154b4/tumblr_inline_ofbr4452601sk4jd9_500.gif
            # https://66.media.tumblr.com/b9395771b2d0435fe4efee926a5a7d9c/tumblr_pg2wu1L9DM1trd056o2_500h.png
            # https://media.tumblr.com/701a535af224f89684d2cfcc097575ef/tumblr_pjsx70RakC1y0gqjko1_1280.pnj
            case _, filename if filename.startswith("tumblr"):
                return TumblrImageUrl(parsed_url=parsable_url)

            case filename, if filename.startswith("avatar_"):
                return TumblrStaticImageUrl(parsed_url=parsable_url)

            # https://25.media.tumblr.com/tumblr_m2dxb8aOJi1rop2v0o1_500.png
            # https://media.tumblr.com/tumblr_m2dxb8aOJi1rop2v0o1_1280.png
            # https://media.tumblr.com/0DNBGJovY5j3smfeQs8nB53z_500.jpg
            # https://media.tumblr.com/tumblr_m24kbxqKAX1rszquso1_1280.jpg
            # https://va.media.tumblr.com/tumblr_pgohk0TjhS1u7mrsl.mp4
            case [_]:
                return TumblrImageUrl(parsed_url=parsable_url)

            case _:
                return None

    @classmethod
    def _match_static(cls, parsable_url: ParsableUrl) -> TumblrUrl | None:
        match parsable_url.url_parts:

            # https://static.tumblr.com/6cc145d8dcf72d6af3a161e3ae9a06b4/c0he0wj/oFaoetjrv/tumblr_static_filename.jpg
            case *_, "tumblr_static_filename.jpg":
                return TumblrStaticImageUrl(parsed_url=parsable_url)

            case _:
                return None

    @classmethod
    def _match_no_subdomain(cls, parsable_url: ParsableUrl) -> TumblrUrl | None:
        match parsable_url.url_parts:
            # https://tumblr.com/munespice/683613396085719040",  # new dashboard link
            # https://www.tumblr.com/yamujiburo/682910938493599744/will-tumblr-let-me-keep-this-up
            case blog_name, post_id, *_ if post_id.isnumeric():
                return TumblrPostUrl(parsed_url=parsable_url,
                                     blog_name=blog_name,
                                     post_id=int(post_id))

            # https://www.tumblr.com/blog/view/artofelaineho/187614935612   # old dashboard link
            case "blog", "view", blog_name, post_id:
                return TumblrPostUrl(parsed_url=parsable_url,
                                     blog_name=blog_name,
                                     post_id=int(post_id))

            # https://www.tumblr.com/blog/view/artofelaineho
            # https://tumblr.com/blog/view/artofelaineho
            case "blog", "view", blog_name:
                return TumblrArtistUrl(parsed_url=parsable_url,
                                       blog_name=blog_name)

            # https://www.tumblr.com/blog/artofelaineho
            # http://tumblr.com/blog/kervalchan
            case "blog", blog_name:
                return TumblrArtistUrl(parsed_url=parsable_url,
                                       blog_name=blog_name)

            # https://www.tumblr.com/dashboard/blog/kohirasan/136686983240
            case "dashboard", "blog", blog_name, post_id:
                return TumblrPostUrl(parsed_url=parsable_url,
                                     blog_name=blog_name,
                                     post_id=int(post_id))

            # https://www.tumblr.com/dashboard/blog/dankwartart
            # https://tumblr.com/dashboard/blog/dankwartart
            case "dashboard", "blog", blog_name:
                return TumblrArtistUrl(parsed_url=parsable_url,
                                       blog_name=blog_name)

            # https://www.tumblr.com/tawni-tailwind
            # https://tumblr.com/tawni-tailwind
            case blog_name, if blog_name not in cls.RESERVED_NAMES:
                return TumblrArtistUrl(parsed_url=parsable_url,
                                       blog_name=blog_name)

            case ("tagged" | "search"), *_:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None

    @classmethod
    def _match_at_subdomain(cls, parsable_url: ParsableUrl) -> TumblrUrl | None:
        match parsable_url.url_parts:

            # https://at.tumblr.com/pizza-and-ramen/118684413624/uqndb20nkyob
            case blog_name, post_id, _title if post_id.isnumeric():
                return TumblrPostUrl(parsed_url=parsable_url,
                                     blog_name=blog_name,
                                     post_id=int(post_id))

            # https://at.tumblr.com/everythingfox/everythingfox-so-sleepy/d842mqsx8lwd
            case blog_name, _title, _redirect_id if blog_name not in cls.RESERVED_NAMES:
                return TumblrArtistUrl(parsed_url=parsable_url,
                                       blog_name=blog_name)

            # https://at.tumblr.com/cyanideqpoison/u2czj612ttzq
            case blog_name, _redirect_id if blog_name not in cls.RESERVED_NAMES:
                return TumblrArtistUrl(parsed_url=parsable_url,
                                       blog_name=blog_name)

            case _:
                return None

    @classmethod
    def _match_with_subdomain(cls, parsable_url: ParsableUrl) -> TumblrUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://merryweather-media.tumblr.com/post/665688699379564544/blue-eyes-white-dragon
            # https://marmaladica.tumblr.com/post/188237914346/saved
            # https://emlan.tumblr.com/post/189469423572/kuro-attempts-to-buy-a-racy-book-at-comiket-but
            # https://superboin.tumblr.com/post/141169066579/photoset_iframe/superboin/tumblr_o45miiAOts1u6rxu8/500/false
            # https://make-do5.tumblr.com/post/619663949657423872
            # http://raspdraws.tumblr.com/image/70021467381
            case ("post" | "image"), post_id, *_ if post_id.isnumeric():
                return TumblrPostUrl(parsed_url=parsable_url,
                                     blog_name=parsable_url.subdomain,
                                     post_id=int(post_id))

            # https://rosarrie.tumblr.com/archive
            # https://solisnotte.tumblr.com/about
            # http://whereisnovember.tumblr.com/tagged/art
            case *_, :
                return TumblrArtistUrl(parsed_url=parsable_url,
                                       blog_name=parsable_url.subdomain)

            case _:
                return None
