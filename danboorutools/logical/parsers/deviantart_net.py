from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.strategies.deviantart import DeviantArtImageUrl


class DeviantartNetParser(UrlParser):
    test_cases = {
        DeviantArtImageUrl: [
            "http://fc09.deviantart.net/fs71/f/2014/055/4/6/for_my_girlfriend_3_by_dfer32-d77ukpi.jpg",

            "http://fc00.deviantart.net/fs71/f/2013/234/d/8/d84e05f26f0695b1153e9dab3a962f16-d6j8jl9.jpg",
            "http://th04.deviantart.net/fs71/PRE/f/2013/337/3/5/35081351f62b432f84eaeddeb4693caf-d6wlrqs.jpg",


            "http://th04.deviantart.net/fs70/300W/f/2009/364/4/d/Alphes_Mimic___Rika_by_Juriesute.png",
            "http://fc02.deviantart.net/fs48/f/2009/186/2/c/Animation_by_epe_tohri.swf",
            "http://fc08.deviantart.net/files/f/2007/120/c/9/Cool_Like_Me_by_47ness.jpg",

            # "http://fc08.deviantart.net/fs71/f/2010/083/0/0/0075a4340efae846f0ea796dc683e8b8.jpg", -> unparsable
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtImageUrl | None:
        instance = DeviantArtImageUrl(parsable_url.url)
        instance.parse_filename(parsable_url.url_parts[-1])
        return instance
