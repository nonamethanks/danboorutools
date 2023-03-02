from danboorutools.logical.extractors.deviantart import DeviantArtArtistUrl, DeviantArtImageUrl, DeviantArtPostUrl, DeviantArtUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class DeviantartComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtUrl | None:
        if parsable_url.subdomain in ["", "www"]:
            return cls._match_username_in_path(parsable_url)
        else:
            return cls._match_username_in_subdomain(parsable_url)

    @staticmethod
    def _match_username_in_path(parsable_url: ParsableUrl) -> DeviantArtUrl | None:
        instance: DeviantArtUrl
        match parsable_url.url_parts:
            # https://www.deviantart.com/deviation/685436408
            case "deviation", deviation_id:
                instance = DeviantArtPostUrl(parsable_url)
                instance.deviation_id = int(deviation_id)
                instance.username = None
                instance.title = None

            # http://www.deviantart.com/download/135944599/Touhou___Suwako_Moriya_Colored_by_Turtle_Chibi.png
            # https://www.deviantart.com/download/549677536/countdown_to_midnight_by_kawacy-d939hwg.jpg?token=92090cd3910d52089b566661e8c2f749755ed5f8&ts=1438535525
            case "download", deviation_id, filename:
                instance = DeviantArtImageUrl(parsable_url)
                instance.deviation_id = int(deviation_id)
                instance.parse_filename(filename)

            # https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408
            # https://www.deviantart.com/bellhenge/art/788000274
            # https://www.deviantart.com/wickellia/art/Anneliese-839666684#comments
            case username, "art", title:
                instance = DeviantArtPostUrl(parsable_url)
                if "-" in title:
                    [instance.title, _, deviation_id] = title.rpartition("-")
                else:
                    instance.title = None
                    deviation_id = title
                try:
                    instance.deviation_id = int(deviation_id)
                except ValueError:
                    instance.deviation_id = int(deviation_id.split("#")[0])
                instance.username = username

            # https://www.deviantart.com/noizave
            # https://deviantart.com/noizave
            # https://www.deviantart.com/nlpsllp/gallery
            case username, *_:
                instance = DeviantArtArtistUrl(parsable_url)
                instance.username = username

            case _:
                return None

        return instance

    @staticmethod
    def _match_username_in_subdomain(parsable_url: ParsableUrl) -> DeviantArtUrl | None:
        instance: DeviantArtUrl
        match parsable_url.url_parts:
            # https://noizave.deviantart.com/art/test-post-please-ignore-685436408
            # https://framboosi.deviantart.com/art/Wendy-commision-for-x4blade-133926691?q=gallery%3Aframboosi%2F12287691\u0026qo=81
            case "art", title:
                instance = DeviantArtPostUrl(parsable_url)
                [instance.title, _, deviation_id] = title.rpartition("-")
                instance.deviation_id = int(deviation_id)
                instance.username = parsable_url.subdomain

            # https://noizave.deviantart.com
            case _:
                instance = DeviantArtArtistUrl(parsable_url)
                instance.username = parsable_url.subdomain

        return instance


class DeviantartNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtImageUrl | None:

        # http://fc09.deviantart.net/fs71/f/2014/055/4/6/for_my_girlfriend_3_by_dfer32-d77ukpi.jpg

        # http://fc00.deviantart.net/fs71/f/2013/234/d/8/d84e05f26f0695b1153e9dab3a962f16-d6j8jl9.jpg
        # http://th04.deviantart.net/fs71/PRE/f/2013/337/3/5/35081351f62b432f84eaeddeb4693caf-d6wlrqs.jpg

        # http://th04.deviantart.net/fs70/300W/f/2009/364/4/d/Alphes_Mimic___Rika_by_Juriesute.png
        # http://fc02.deviantart.net/fs48/f/2009/186/2/c/Animation_by_epe_tohri.swf
        # http://fc08.deviantart.net/files/f/2007/120/c/9/Cool_Like_Me_by_47ness.jpg

        # http://fc08.deviantart.net/fs71/f/2010/083/0/0/0075a4340efae846f0ea796dc683e8b8.jpg -> unparsable
        instance = DeviantArtImageUrl(parsable_url)
        instance.parse_filename(parsable_url.url_parts[-1])
        return instance


class DaportfolioComParser(UrlParser):
    domains = ["daportfolio.com", "artworkfolio.com"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtArtistUrl | None:
        # http://nemupanart.daportfolio.com
        # http://regi-chan.artworkfolio.com

        instance = DeviantArtArtistUrl(parsable_url)
        instance.username = parsable_url.subdomain
        return instance


class FavMeParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtPostUrl | None:
        # https://fav.me/dbc3a48
        # https://www.fav.me/dbc3a48
        instance = DeviantArtPostUrl(parsable_url)
        instance.deviation_id = int(parsable_url.url_parts[0], 36)
        instance.title = None
        instance.username = None
        return instance
