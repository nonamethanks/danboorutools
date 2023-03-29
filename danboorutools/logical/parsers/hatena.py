from urllib.parse import unquote

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.hatena import (
    HatenaArtistImageUrl,
    HatenaBlogPostUrl,
    HatenaBlogUrl,
    HatenaFotolifeArtistUrl,
    HatenaFotolifePostUrl,
    HatenaImageUrl,
    HatenaProfileUrl,
    HatenaUgomemoUrl,
    HatenaUrl,
)
from danboorutools.models.url import UselessUrl


class HatenaParser(UrlParser):
    domains = ["hatena.ne.jp", "hatena.com", "hatenadiary.org", "hatenablog.com"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> HatenaUrl | UselessUrl | None:
        if parsable_url.url_parts == ["login"]:
            unquoted = unquote(parsable_url.query["blog"])
            return cls.match_url(ParsableUrl(unquoted))

        elif parsable_url.domain in ["hatena.ne.jp", "hatena.com"]:
            return cls._match_hatena_ne_jp(parsable_url)

        elif parsable_url.domain in ["hatenadiary.org", "hatenablog.com"]:
            return cls._match_hatena_blog_sites(parsable_url)
        else:
            return None

    @classmethod
    def _match_hatena_ne_jp(cls, parsable_url: ParsableUrl) -> HatenaUrl | UselessUrl | None:
        if parsable_url.subdomain in ["f", "img.f"]:
            return cls._match_fotolife_subdomain(parsable_url)

        # http://ugomemo.hatena.ne.jp/167427A0CEF89DA2@DSi/
        elif parsable_url.subdomain == "ugomemo":
            user_id, = parsable_url.url_parts
            return HatenaUgomemoUrl(parsed_url=parsable_url,
                                    user_id=user_id)

        elif parsable_url.subdomain in ["profile", "h", "b", "q", "", "www"] or parsable_url.subdomain.endswith(".g"):
            return cls._match_profile_subdomains(parsable_url)

        elif parsable_url.subdomain == "blog":
            return cls._match_blog_subdomain(parsable_url)

        elif parsable_url.subdomain == "d":
            return cls._match_d_subdomain(parsable_url)

        elif parsable_url.subdomain == "blog":
            # https://blog.hatena.ne.jp/login?blog=https%3A%2F%2Fam-1-00.hatenadiary.org%2F
            unquoted = unquote(parsable_url.query["blog"])
            return cls.match_url(ParsableUrl(unquoted))
        else:
            return None

    @staticmethod
    def _match_fotolife_subdomain(parsable_url: ParsableUrl) -> HatenaUrl | None:
        match parsable_url.url_parts:
            case username, post_id:
                # https://f.hatena.ne.jp/msmt1118/20190927210959
                if post_id.isnumeric():
                    return HatenaFotolifePostUrl(parsed_url=parsable_url,
                                                 post_id=int(post_id),
                                                 username=username)

                # http://f.hatena.ne.jp/kazeshima/風島１８/
                else:
                    return HatenaFotolifeArtistUrl(parsed_url=parsable_url,
                                                   username=username)

            # https://f.hatena.ne.jp/msmt1118
            case username, :
                return HatenaFotolifeArtistUrl(parsed_url=parsable_url,
                                               username=username)

            # http://img.f.hatena.ne.jp/images/fotolife/m/mauuuuuu/
            case "images", "fotolife", _, username:
                return HatenaFotolifeArtistUrl(parsed_url=parsable_url,
                                               username=username)

            # http://f.hatena.ne.jp/images/fotolife/b/beni/20100403/
            case "images", "fotolife", _, username, _:
                return HatenaFotolifeArtistUrl(parsed_url=parsable_url,
                                               username=username)

            # http://img.f.hatena.ne.jp/images/fotolife/a/asasow/20080928/20080928002141.jpg
            # -> https://cdn-ak.f.st-hatena.com/images/fotolife/a/asasow/20080928/20080928002141.jpg
            case "images", "fotolife", _, username, _date, _image_id:
                return HatenaImageUrl(parsed_url=parsable_url)

            case _:
                return None

    @staticmethod
    def _match_profile_subdomains(parsable_url: ParsableUrl) -> HatenaProfileUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://profile.hatena.ne.jp/gekkakou616/
            # http://www.hatena.ne.jp/ranpha/
            # all of these subdomains are dead or useless, no reason to keep them all separate
            # http://kokage.g.hatena.ne.jp/kokage/
            # http://b.hatena.ne.jp/kat_cloudair/
            # http://h.hatena.ne.jp/jandare-210/
            # https://q.hatena.ne.jp/ten59
            case username, if username not in ["id"]:
                return HatenaProfileUrl(parsed_url=parsable_url,
                                        username=username)

            # http://h.hatena.ne.jp/id/rera
            case "id", username:
                return HatenaProfileUrl(parsed_url=parsable_url,
                                        username=username)

            # https://profile.hatena.ne.jp/Lukecarter/profile
            case username, "profile":
                return HatenaProfileUrl(parsed_url=parsable_url,
                                        username=username)

    @staticmethod
    def _match_d_subdomain(parsable_url: ParsableUrl) -> HatenaUrl | UselessUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case "keyword", *_:
                return UselessUrl(parsed_url=parsable_url)

            # http://d.hatena.ne.jp/gentoji/00000204/1282974942
            case username, post_date_str, post_id:
                return HatenaBlogPostUrl(parsed_url=parsable_url,
                                         post_date_str=post_date_str,
                                         username=username.replace("_", "-"),
                                         domain="hatenadiary.org",
                                         post_id=post_id)

            # http://d.hatena.ne.jp/asakuma776/archive?word=沙谷
            # http://d.hatena.ne.jp/kab_studio/searchdiary?word=%2a%5b%b3%a8%5d
            # http://d.hatena.ne.jp/toh_azuma/about
            case username, ("archive" | "searchdiary" | "about"):
                return HatenaBlogUrl(parsed_url=parsable_url,
                                     domain="hatenadiary.org",
                                     username=username.replace("_", "-"))

            # http://d.hatena.ne.jp/votamochi/20091015  # not normalizable
            case username, post_date if post_date.isnumeric():
                return HatenaBlogUrl(parsed_url=parsable_url,
                                     domain="hatenadiary.org",
                                     username=username.replace("_", "-"))

            # http://d.hatena.ne.jp/ten59/
            case username, :
                return HatenaBlogUrl(parsed_url=parsable_url,
                                     domain="hatenadiary.org",
                                     username=username.replace("_", "-"))

            # http://d.hatena.ne.jp/images/diary/t/taireru/
            case "images", "diary", char, username if len(char) == 1:
                return HatenaBlogUrl(parsed_url=parsable_url,
                                     domain="hatenadiary.org",
                                     username=username.replace("_", "-"))

            # http://d.hatena.ne.jp/images/diary/t/tajirin/tajirin.jpg
            # -> https://cdn.profile-image.st-hatena.com/users/tajirin/profile_256x256.png
            case "images", "diary", char, username, _filename if len(char) == 1:
                return HatenaArtistImageUrl(parsed_url=parsable_url,
                                            username=username.replace("_", "-"))

            case _:
                return None

    @ staticmethod
    def _match_blog_subdomain(parsable_url: ParsableUrl) -> HatenaBlogUrl | None:
        match parsable_url.url_parts:
            # http://blog.hatena.ne.jp/daftomiken/
            case username, :
                return HatenaBlogUrl(parsed_url=parsable_url,
                                     username=username,
                                     domain="hatenablog.com")
            case _:
                return None

    @ staticmethod
    def _match_hatena_blog_sites(parsable_url: ParsableUrl) -> HatenaUrl | UselessUrl | None:  # type: ignore[return]
        if parsable_url.subdomain in ["www", ""]:
            return UselessUrl(parsed_url=parsable_url)

        match parsable_url.url_parts:
            # https://fujikino.hatenablog.com/entry/2018/01/27/041829
            case "entry", year, month, day, post_id if post_id.isnumeric() and len(year) == 4 and len(month) == 2 and len(day) == 2:
                return HatenaBlogPostUrl(parsed_url=parsable_url,
                                         post_date_str=f"{year}/{month}/{day}",
                                         username=parsable_url.subdomain,
                                         domain=parsable_url.domain,
                                         post_id=post_id)

            # https://votamochi.hatenadiary.org/entries/2009/10/15  # this lacks post id, can't be normalized
            case "entries", _year, _month, _day if len(_year) == 4 and len(_month) == 2 and len(_day) == 2:
                return HatenaBlogUrl(parsed_url=parsable_url,
                                     domain=parsable_url.domain,
                                     username=parsable_url.subdomain)

            # http://tennendojo.hatenablog.com/entry/20121224/1356369437
            # https://votamochi.hatenadiary.org/entry/20091015/1255636487
            case "entry", post_date_str, post_id if post_id.isnumeric() and post_date_str.isnumeric():
                return HatenaBlogPostUrl(parsed_url=parsable_url,
                                         post_date_str=post_date_str,
                                         username=parsable_url.subdomain,
                                         domain=parsable_url.domain,
                                         post_id=post_id)

            # http://satsukiyasan.hatenablog.com/about
            case [] | ["about"]:
                return HatenaBlogUrl(parsed_url=parsable_url,
                                     username=parsable_url.subdomain,
                                     domain=parsable_url.domain)
            case _:
                return None
