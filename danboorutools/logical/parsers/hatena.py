from urllib.parse import unquote

from danboorutools.logical.extractors.hatena import (
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
from danboorutools.logical.parsers import ParsableUrl, UrlParser
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
        instance: HatenaUrl
        if parsable_url.subdomain in ["f", "img.f"]:
            return cls._match_fotolife_subdomain(parsable_url)

        # http://ugomemo.hatena.ne.jp/167427A0CEF89DA2@DSi/
        elif parsable_url.subdomain == "ugomemo":
            instance = HatenaUgomemoUrl(parsable_url)
            [instance.user_id] = parsable_url.url_parts
            return instance

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
        instance: HatenaUrl
        match parsable_url.url_parts:
            case username, post_id:
                # https://f.hatena.ne.jp/msmt1118/20190927210959
                if post_id.isnumeric():
                    instance = HatenaFotolifePostUrl(parsable_url)
                    instance.post_id = int(post_id)
                    instance.username = username
                # http://f.hatena.ne.jp/kazeshima/風島１８/
                else:
                    instance = HatenaFotolifeArtistUrl(parsable_url)
                    instance.username = username

            # https://f.hatena.ne.jp/msmt1118
            case username, :
                instance = HatenaFotolifeArtistUrl(parsable_url)
                instance.username = username

            # http://img.f.hatena.ne.jp/images/fotolife/m/mauuuuuu/
            case "images", "fotolife", _, username:
                instance = HatenaFotolifeArtistUrl(parsable_url)
                instance.username = username

            # http://f.hatena.ne.jp/images/fotolife/b/beni/20100403/
            case "images", "fotolife", _, username, _:
                instance = HatenaFotolifeArtistUrl(parsable_url)
                instance.username = username

            # http://img.f.hatena.ne.jp/images/fotolife/a/asasow/20080928/20080928002141.jpg
            # -> https://cdn-ak.f.st-hatena.com/images/fotolife/a/asasow/20080928/20080928002141.jpg
            case "images", "fotolife", _, username, _date, _image_id:
                instance = HatenaImageUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_profile_subdomains(parsable_url: ParsableUrl) -> HatenaProfileUrl | None:
        instance: HatenaProfileUrl
        match parsable_url.url_parts:
            # https://profile.hatena.ne.jp/gekkakou616/
            # http://www.hatena.ne.jp/ranpha/
            # all of these subdomains are dead or useless, no reason to keep them all separate
            # http://kokage.g.hatena.ne.jp/kokage/
            # http://b.hatena.ne.jp/kat_cloudair/
            # http://h.hatena.ne.jp/jandare-210/
            # https://q.hatena.ne.jp/ten59
            case username, if username not in ["id"]:
                instance = HatenaProfileUrl(parsable_url)
                instance.username = username

            # http://h.hatena.ne.jp/id/rera
            case "id", username:
                instance = HatenaProfileUrl(parsable_url)
                instance.username = username

            # https://profile.hatena.ne.jp/Lukecarter/profile
            case username, "profile":
                instance = HatenaProfileUrl(parsable_url)
                instance.username = username

        return instance

    @staticmethod
    def _match_d_subdomain(parsable_url: ParsableUrl) -> HatenaUrl | UselessUrl | None:
        instance: HatenaUrl

        match parsable_url.url_parts:
            case "keyword", *_:
                return UselessUrl(parsable_url)

            # http://d.hatena.ne.jp/gentoji/00000204/1282974942
            case username, post_date_str, post_id:
                instance = HatenaBlogPostUrl(parsable_url)
                instance.username = username
                instance.post_id = post_id
                instance.post_date_str = post_date_str

            # http://d.hatena.ne.jp/asakuma776/archive?word=沙谷
            # http://d.hatena.ne.jp/kab_studio/searchdiary?word=%2a%5b%b3%a8%5d
            # http://d.hatena.ne.jp/toh_azuma/about
            case username, ("archive" | "searchdiary" | "about"):
                instance = HatenaBlogUrl(parsable_url)
                instance.username = username

            # http://d.hatena.ne.jp/votamochi/20091015  # not normalizable
            case username, post_date if post_date.isnumeric():
                instance = HatenaBlogUrl(parsable_url)
                instance.username = username

            # http://d.hatena.ne.jp/ten59/
            case username, :
                instance = HatenaBlogUrl(parsable_url)
                instance.username = username

            # http://d.hatena.ne.jp/images/diary/t/taireru/
            case "images", "diary", char, username if len(char) == 1:
                instance = HatenaBlogUrl(parsable_url)
                instance.username = username

            # http://d.hatena.ne.jp/images/diary/t/tajirin/tajirin.jpg
            # -> https://cdn.profile-image.st-hatena.com/users/tajirin/profile_256x256.png
            case "images", "diary", char, username, _filename if len(char) == 1:
                instance = HatenaArtistImageUrl(parsable_url)
                instance.username = username
                return instance

            case _:
                return None

        instance.username = instance.username.replace("_", "-")  # type: ignore[attr-defined] # fuck off retard
        instance.domain = "hatenadiary.org"  # type: ignore[attr-defined] # fuck off retard
        return instance

    @staticmethod
    def _match_blog_subdomain(parsable_url: ParsableUrl) -> HatenaBlogUrl | None:
        instance: HatenaBlogUrl
        match parsable_url.url_parts:
            # http://blog.hatena.ne.jp/daftomiken/
            case username, :
                instance = HatenaBlogUrl(parsable_url)
                instance.username = username
                instance.domain = "hatenablog.com"

        return instance

    @staticmethod
    def _match_hatena_blog_sites(parsable_url: ParsableUrl) -> HatenaUrl | UselessUrl | None:
        if parsable_url.subdomain in ["www", ""]:
            return UselessUrl(parsable_url)

        instance: HatenaBlogUrl | HatenaBlogPostUrl
        match parsable_url.url_parts:
            # https://fujikino.hatenablog.com/entry/2018/01/27/041829
            case "entry", year, month, day, post_id if post_id.isnumeric() and len(year) == 4 and len(month) == 2 and len(day) == 2:
                instance = HatenaBlogPostUrl(parsable_url)
                instance.post_date_str = f"{year}/{month}/{day}"
                instance.post_id = post_id

            # https://votamochi.hatenadiary.org/entries/2009/10/15  # this lacks post id, can't be normalized
            case "entries", _year, _month, _day if len(_year) == 4 and len(_month) == 2 and len(_day) == 2:
                instance = HatenaBlogUrl(parsable_url)

            # http://tennendojo.hatenablog.com/entry/20121224/1356369437
            # https://votamochi.hatenadiary.org/entry/20091015/1255636487
            case "entry", post_date_str, post_id if post_id.isnumeric() and post_date_str.isnumeric():
                instance = HatenaBlogPostUrl(parsable_url)
                instance.post_date_str = post_date_str
                instance.post_id = post_id

            # http://satsukiyasan.hatenablog.com/about
            case [] | ["about"]:
                instance = HatenaBlogUrl(parsable_url)
            case _:
                return None

        instance.username = parsable_url.subdomain
        instance.domain = parsable_url.domain
        return instance
