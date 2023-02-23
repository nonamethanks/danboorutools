
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://www.deviantart.com/deviation/685436408": "https://www.deviantart.com/deviation/685436408",

    "https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408": "https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408",
    "https://www.deviantart.com/bellhenge/art/788000274": "https://www.deviantart.com/bellhenge/art/788000274",

    "https://noizave.deviantart.com/art/test-post-please-ignore-685436408": "https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408",
    "https://framboosi.deviantart.com/art/Wendy-commision-for-x4blade-133926691?q=gallery%3Aframboosi%2F12287691\u0026qo=81": "https://www.deviantart.com/framboosi/art/Wendy-commision-for-x4blade-133926691",
    "https://www.deviantart.com/wickellia/art/Anneliese-839666684#comments": "https://www.deviantart.com/wickellia/art/Anneliese-839666684",

    # "http://www.deviantart.com/download/135944599/Touhou___Suwako_Moriya_Colored_by_Turtle_Chibi.png": "http://www.deviantart.com/download/135944599/Touhou___Suwako_Moriya_Colored_by_Turtle_Chibi.png",
    # "https://www.deviantart.com/download/549677536/countdown_to_midnight_by_kawacy-d939hwg.jpg?token=92090cd3910d52089b566661e8c2f749755ed5f8&ts=1438535525": "https://www.deviantart.com/download/549677536/countdown_to_midnight_by_kawacy-d939hwg.jpg?token=92090cd3910d52089b566661e8c2f749755ed5f8&ts=1438535525",

    # "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/52c4a3ad-d416-42f0-90f6-570983e36797/dczr28f-bd255304-01bf-4765-8cd3-e53983d3f78a.jpg",
    # "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/8b472d70-a0d6-41b5-9a66-c35687090acc/d23jbr4-8a06af02-70cb-46da-8a96-42a6ba73cdb4.jpg/v1/fill/w_786,h_1017,q_70,strp/silverhawks_quicksilver_by_edsfox_d23jbr4-pre.jpg",

    # "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/76098ac8-04ab-4784-b382-88ca082ba9b1/d9x7lmk-595099de-fe8f-48e5-9841-7254f9b2ab8d.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvNzYwOThhYzgtMDRhYi00Nzg0LWIzODItODhjYTA4MmJhOWIxXC9kOXg3bG1rLTU5NTA5OWRlLWZlOGYtNDhlNS05ODQxLTcyNTRmOWIyYWI4ZC5wbmcifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.KFOVXAiF8MTlLb3oM-FlD0nnDvODmjqEhFYN5I2X5Bc",
    # "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/fe7ab27f-7530-4252-99ef-2baaf81b36fd/dddf6pe-1a4a091c-768c-4395-9465-5d33899be1eb.png/v1/fill/w_800,h_1130,q_80,strp/stay_hydrated_and_in_the_shade_by_raikoart_dddf6pe-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9MTEzMCIsInBhdGgiOiJcL2ZcL2ZlN2FiMjdmLTc1MzAtNDI1Mi05OWVmLTJiYWFmODFiMzZmZFwvZGRkZjZwZS0xYTRhMDkxYy03NjhjLTQzOTUtOTQ2NS01ZDMzODk5YmUxZWIucG5nIiwid2lkdGgiOiI8PTgwMCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.J0W4k-iV6Mg8Kt_5Lr_L_JbBq4lyr7aCausWWJ_Fsbw",

    # "http://fc09.deviantart.net/fs71/f/2014/055/4/6/for_my_girlfriend_3_by_dfer32-d77ukpi.jpg",

    # "http://fc00.deviantart.net/fs71/f/2013/234/d/8/d84e05f26f0695b1153e9dab3a962f16-d6j8jl9.jpg",
    # "http://th04.deviantart.net/fs71/PRE/f/2013/337/3/5/35081351f62b432f84eaeddeb4693caf-d6wlrqs.jpg",


    # "http://th04.deviantart.net/fs70/300W/f/2009/364/4/d/Alphes_Mimic___Rika_by_Juriesute.png",
    # "http://fc02.deviantart.net/fs48/f/2009/186/2/c/Animation_by_epe_tohri.swf",
    # "http://fc08.deviantart.net/files/f/2007/120/c/9/Cool_Like_Me_by_47ness.jpg",

    "https://www.deviantart.com/noizave": "https://www.deviantart.com/noizave",
    "https://deviantart.com/noizave": "https://www.deviantart.com/noizave",
    "https://www.deviantart.com/nlpsllp/gallery": "https://www.deviantart.com/nlpsllp",

    "https://noizave.deviantart.com": "https://www.deviantart.com/noizave",
    "http://nemupanart.daportfolio.com": "https://www.deviantart.com/nemupanart",
    "http://regi-chan.artworkfolio.com": "https://www.deviantart.com/regi-chan",

    "https://fav.me/dbc3a48": "https://www.deviantart.com/deviation/28983606776",
    "https://www.fav.me/dbc3a48": "https://www.deviantart.com/deviation/28983606776",
}

for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
