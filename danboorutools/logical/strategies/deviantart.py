from danboorutools.models.url import ArtistUrl, AssetUrl, PostUrl, RedirectUrl
from danboorutools.util.misc import compile_url

REGEX_IMAGE = compile_url(
    r"https?:\/\/\w+\.deviantart\.(net|com)\/(\w+\/)+(?P<filename>[\w]+(?:-d(?P<deviation_b36>\w{6}))?\.\w+)"
)
REGEX_IMAGE_WIXMP = compile_url(
    r"https?:\/\/[\w-]+\.wixmp.com\/(?:[\w-]+\/)+d(?P<deviation_b36>\w{6})[\w-]+\.\w+(?:(?:\/[\w,]+)+\/(?P<filename>[\w-]+\.\w+))?"
)
REGEX_POST = compile_url(
    r"https?:\/\/(?:(?P<artist_name>(?!www)[\w-]+)\.(?:deviantart)\.com|(?:\www\.)?deviantart\.com\/)"
    r"(?:(?!download)(?:deviation|(?P<artist_name>\w+)))?"
    r"\/(?:(?P<post_id>\d+)|art\/(?P<title>[\w-]+)-(?P<post_id>\d+)|deviation\/(?P<post_id>\d+))"
)
REGEX_ARTIST = compile_url(
    r"https?:\/\/(?:",
    r"(?P<artist_name>(?!www)[\w-]+)\.(?:deviantart|daportfolio|artworkfolio)\.com"
    r"|"
    r"(?:\www\.)?deviantart\.com\/(?P<artist_name>(?!deviation|download)\w+)"
    r")(?:\/(?:(?!art)\w+(?:\/.*)?)?)?$"
)
REGEX_FAVME = compile_url(r"https:\/\/(?:www\.)?fav\.me\/d(?P<deviation_b36>\w+)")
REGEX_STASH = compile_url(r"https:\/\/sta\.sh\/(?P<stash_id>\w+)")


class DeviantArtPostUrl(PostUrl):
    test_cases = [
        "https://www.deviantart.com/deviation/685436408",
        "https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408",
        "https://noizave.deviantart.com/art/test-post-please-ignore-685436408",
    ]
    domains = ["deviantart.com"]
    pattern = REGEX_POST
    normalization = "https://www..deviantart.com/{artist_name}/art/{title}-{post_id}"
    id_name = "post_id"


class DeviantArtArtistUrl(ArtistUrl):
    test_cases = [
        "https://www.deviantart.com/noizave",
        "https://deviantart.com/noizave",
        "https://www.deviantart.com/nlpsllp/gallery",

        "https://noizave.deviantart.com",
        "http://nemupanart.daportfolio.com",
        "http://regi-chan.artworkfolio.com",
    ]
    domains = ["deviantart.com", "daportfolio.com", "artworkfolio.com"]
    pattern = REGEX_ARTIST
    normalization = "https://{artist_name}.deviantart.com"
    id_name = "artist_name"


class DeviantArtImageUrl(AssetUrl):
    test_cases = [
        "http://orig12.deviantart.net/9b69/f/2017/023/7/c/illustration___tokyo_encount_oei__by_melisaongmiqin-dawi58s.png",
        "http://pre15.deviantart.net/81de/th/pre/f/2015/063/5/f/inha_by_inhaestudios-d8kfzm5.jpg",
        "http://th00.deviantart.net/fs71/PRE/f/2014/065/3/b/goruto_by_xyelkiltrox-d797tit.png",
        "http://fc00.deviantart.net/fs71/f/2013/234/d/8/d84e05f26f0695b1153e9dab3a962f16-d6j8jl9.jpg",
        "http://th04.deviantart.net/fs71/PRE/f/2013/337/3/5/35081351f62b432f84eaeddeb4693caf-d6wlrqs.jpg",

        "http://www.deviantart.com/download/135944599/Touhou___Suwako_Moriya_Colored_by_Turtle_Chibi.png",
        "https://www.deviantart.com/download/549677536/countdown_to_midnight_by_kawacy-d939hwg.jpg?token=92090cd3910d52089b566661e8c2f749755ed5f8&ts=1438535525",
    ]
    domains = ["deviantart.com", "deviantart.net"]
    pattern = REGEX_IMAGE
    id_name = ""
    # TODO: implement parsing filename to extract post etc


class DeviantArtWixmpImage(AssetUrl):
    test_cases = [
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/52c4a3ad-d416-42f0-90f6-570983e36797/dczr28f-bd255304-01bf-4765-8cd3-e53983d3f78a.jpg",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/8b472d70-a0d6-41b5-9a66-c35687090acc/d23jbr4-8a06af02-70cb-46da-8a96-42a6ba73cdb4.jpg/v1/fill/w_786,h_1017,q_70,strp/silverhawks_quicksilver_by_edsfox_d23jbr4-pre.jpg",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/76098ac8-04ab-4784-b382-88ca082ba9b1/d9x7lmk-595099de-fe8f-48e5-9841-7254f9b2ab8d.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvNzYwOThhYzgtMDRhYi00Nzg0LWIzODItODhjYTA4MmJhOWIxXC9kOXg3bG1rLTU5NTA5OWRlLWZlOGYtNDhlNS05ODQxLTcyNTRmOWIyYWI4ZC5wbmcifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.KFOVXAiF8MTlLb3oM-FlD0nnDvODmjqEhFYN5I2X5Bc",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/fe7ab27f-7530-4252-99ef-2baaf81b36fd/dddf6pe-1a4a091c-768c-4395-9465-5d33899be1eb.png/v1/fill/w_800,h_1130,q_80,strp/stay_hydrated_and_in_the_shade_by_raikoart_dddf6pe-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9MTEzMCIsInBhdGgiOiJcL2ZcL2ZlN2FiMjdmLTc1MzAtNDI1Mi05OWVmLTJiYWFmODFiMzZmZFwvZGRkZjZwZS0xYTRhMDkxYy03NjhjLTQzOTUtOTQ2NS01ZDMzODk5YmUxZWIucG5nIiwid2lkdGgiOiI8PTgwMCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.J0W4k-iV6Mg8Kt_5Lr_L_JbBq4lyr7aCausWWJ_Fsbw",
    ]
    domains = ["wixmp.com"]
    pattern = REGEX_IMAGE_WIXMP
    id_name = ""
    # TODO: implement parsing filename to extract post etc


class FavMeUrl(RedirectUrl):
    test_cases = [
        "https://fav.me/dbc3a48",
        "https://www.fav.me/dbc3a48",
    ]
    domains = ["fav.me"]
    pattern = REGEX_FAVME
    id_name = "deviation_b36"
    # TODO: this doesn't need to do a redirection, it can be converted to a DeviantArtImageUrl which can then fetch the post as required


class StashUrl(PostUrl):
    test_cases = [
        "https://sta.sh/21leo8mz87ue",  # (folder)
        "https://sta.sh/2uk0v5wabdt",  # (subfolder)
        "https://sta.sh/0wxs31o7nn2",  # (single image)
        # Ref: https://www.deviantartsupport.com/en/article/what-is-stash-3391708
        # Ref: https://www.deviantart.com/developers/http/v1/20160316/stash_item/4662dd8b10e336486ea9a0b14da62b74
    ]
    domains = ["sta.sh"]
    pattern = REGEX_STASH
    normalization = "https://sta.sh/{stash_id}"
    id_name = "stash_id"
