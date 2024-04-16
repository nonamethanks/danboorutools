import pytest

from danboorutools.logical.urls.deviantart import DeviantArtArtistUrl, DeviantArtImageUrl, DeviantArtPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    DeviantArtPostUrl: {
        "https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408": "https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408",
        "https://www.deviantart.com/bellhenge/art/788000274": "https://www.deviantart.com/bellhenge/art/788000274",

        "https://noizave.deviantart.com/art/test-post-please-ignore-685436408": "https://www.deviantart.com/noizave/art/test-post-please-ignore-685436408",
        "https://framboosi.deviantart.com/art/Wendy-commision-for-x4blade-133926691?q=gallery%3Aframboosi%2F12287691\u0026qo=81": "https://www.deviantart.com/framboosi/art/Wendy-commision-for-x4blade-133926691",
        "https://www.deviantart.com/wickellia/art/Anneliese-839666684#comments": "https://www.deviantart.com/wickellia/art/Anneliese-839666684",
        "https://fav.me/dbc3a48": "https://www.deviantart.com/deviation/28983606776",
        "https://www.fav.me/dbc3a48": "https://www.deviantart.com/deviation/28983606776",
        "https://www.deviantart.com/deviation/685436408": "https://www.deviantart.com/deviation/685436408",

    },
    DeviantArtImageUrl: {
        "http://www.deviantart.com/download/135944599/Touhou___Suwako_Moriya_Colored_by_Turtle_Chibi.png": "",
        "https://www.deviantart.com/download/549677536/countdown_to_midnight_by_kawacy-d939hwg.jpg?token=92090cd3910d52089b566661e8c2f749755ed5f8&ts=1438535525": "",

        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/52c4a3ad-d416-42f0-90f6-570983e36797/dczr28f-bd255304-01bf-4765-8cd3-e53983d3f78a.jpg": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/52c4a3ad-d416-42f0-90f6-570983e36797/dczr28f-bd255304-01bf-4765-8cd3-e53983d3f78a.jpg",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/8b472d70-a0d6-41b5-9a66-c35687090acc/d23jbr4-8a06af02-70cb-46da-8a96-42a6ba73cdb4.jpg/v1/fill/w_786,h_1017,q_70,strp/silverhawks_quicksilver_by_edsfox_d23jbr4-pre.jpg": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/8b472d70-a0d6-41b5-9a66-c35687090acc/d23jbr4-8a06af02-70cb-46da-8a96-42a6ba73cdb4.jpg",

        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/76098ac8-04ab-4784-b382-88ca082ba9b1/d9x7lmk-595099de-fe8f-48e5-9841-7254f9b2ab8d.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvNzYwOThhYzgtMDRhYi00Nzg0LWIzODItODhjYTA4MmJhOWIxXC9kOXg3bG1rLTU5NTA5OWRlLWZlOGYtNDhlNS05ODQxLTcyNTRmOWIyYWI4ZC5wbmcifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.KFOVXAiF8MTlLb3oM-FlD0nnDvODmjqEhFYN5I2X5Bc": "",

        "http://fc09.deviantart.net/fs71/f/2014/055/4/6/for_my_girlfriend_3_by_dfer32-d77ukpi.jpg": "",

        "http://fc00.deviantart.net/fs71/f/2013/234/d/8/d84e05f26f0695b1153e9dab3a962f16-d6j8jl9.jpg": "",
        "http://th04.deviantart.net/fs71/PRE/f/2013/337/3/5/35081351f62b432f84eaeddeb4693caf-d6wlrqs.jpg": "",

        "http://th04.deviantart.net/fs70/300W/f/2009/364/4/d/Alphes_Mimic___Rika_by_Juriesute.png": "",
        "http://fc02.deviantart.net/fs48/f/2009/186/2/c/Animation_by_epe_tohri.swf": "",
        "http://fc08.deviantart.net/files/f/2007/120/c/9/Cool_Like_Me_by_47ness.jpg": "",

        # http://fc08.deviantart.net/fs71/f/2010/083/0/0/0075a4340efae846f0ea796dc683e8b8.jpg -> unparsable

        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/d8995973-0b32-4a7d-8cd8-d847d083689a/d797tit-1eac22e0-38b6-4eae-adcb-1b72843fd62a.png/v1/fill/w_720,h_1110,q_75,strp/goruto_by_xyelkiltrox-d797tit.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl0sIm9iaiI6W1t7InBhdGgiOiIvZi9kODk5NTk3My0wYjMyLTRhN2QtOGNkOC1kODQ3ZDA4MzY4OWEvZDc5N3RpdC0xZWFjMjJlMC0zOGI2LTRlYWUtYWRjYi0xYjcyODQzZmQ2MmEucG5nIiwid2lkdGgiOiI8PTcyMCIsImhlaWdodCI6Ijw9MTExMCJ9XV19.vSlSlntfQQ9qwJBv8mldhKRtllVAhUESfQfo6P0lHsU": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/d8995973-0b32-4a7d-8cd8-d847d083689a/d797tit-1eac22e0-38b6-4eae-adcb-1b72843fd62a.png",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/7af88dfc-1056-4b79-9572-04ef3fdbba49/d6wlrqs-29b97fda-3c46-4205-bd90-f54007db0b04.jpg/v1/fill/w_730,h_1095,q_75,strp/35081351f62b432f84eaeddeb4693caf-d6wlrqs.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwic3ViIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl0sIm9iaiI6W1t7InBhdGgiOiIvZi83YWY4OGRmYy0xMDU2LTRiNzktOTU3Mi0wNGVmM2ZkYmJhNDkvZDZ3bHJxcy0yOWI5N2ZkYS0zYzQ2LTQyMDUtYmQ5MC1mNTQwMDdkYjBiMDQuanBnIiwid2lkdGgiOiI8PTczMCIsImhlaWdodCI6Ijw9MTA5NSJ9XV19.VXLzB4r28uWeVruI6QFn_6klVgm2YXG3_k6AWNXzRMk": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/7af88dfc-1056-4b79-9572-04ef3fdbba49/d6wlrqs-29b97fda-3c46-4205-bd90-f54007db0b04.jpg",
        "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/fe7ab27f-7530-4252-99ef-2baaf81b36fd/dddf6pe-1a4a091c-768c-4395-9465-5d33899be1eb.png/v1/fill/w_800,h_1130,q_80,strp/stay_hydrated_and_in_the_shade_by_raikoart_dddf6pe-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9MTEzMCIsInBhdGgiOiJcL2ZcL2ZlN2FiMjdmLTc1MzAtNDI1Mi05OWVmLTJiYWFmODFiMzZmZFwvZGRkZjZwZS0xYTRhMDkxYy03NjhjLTQzOTUtOTQ2NS01ZDMzODk5YmUxZWIucG5nIiwid2lkdGgiOiI8PTgwMCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.J0W4k-iV6Mg8Kt_5Lr_L_JbBq4lyr7aCausWWJ_Fsbw": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/fe7ab27f-7530-4252-99ef-2baaf81b36fd/dddf6pe-1a4a091c-768c-4395-9465-5d33899be1eb.png/v1/fill/w_800,h_1130/stay_hydrated_and_in_the_shade_by_raikoart_dddf6pe-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9MTEzMCIsInBhdGgiOiJcL2ZcL2ZlN2FiMjdmLTc1MzAtNDI1Mi05OWVmLTJiYWFmODFiMzZmZFwvZGRkZjZwZS0xYTRhMDkxYy03NjhjLTQzOTUtOTQ2NS01ZDMzODk5YmUxZWIucG5nIiwid2lkdGgiOiI8PTgwMCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.J0W4k-iV6Mg8Kt_5Lr_L_JbBq4lyr7aCausWWJ_Fsbw",
    },
    DeviantArtArtistUrl: {
        "https://www.deviantart.com/noizave": "https://www.deviantart.com/noizave",
        "https://deviantart.com/noizave": "https://www.deviantart.com/noizave",
        "https://www.deviantart.com/nlpsllp/gallery": "https://www.deviantart.com/nlpsllp",

        "https://noizave.deviantart.com": "https://www.deviantart.com/noizave",
        "http://nemupanart.daportfolio.com": "https://www.deviantart.com/nemupanart",
        "http://regi-chan.artworkfolio.com": "https://www.deviantart.com/regi-chan",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestDeviantArtArtistUrl(_TestArtistUrl):
    url_string = "https://www.deviantart.com/oneori"
    url_type = DeviantArtArtistUrl
    url_properties = dict(username="oneori")
    primary_names = ["oneori"]
    secondary_names = []
    related = [
        "https://www.facebook.com/KittyRaymson/",
        "https://www.instagram.com/o_neo_ri",
        "https://www.youtube.com/channel/UCqiIF06TpxsxuIEuRSNsajw",
        "https://twitter.com/o_Neo_ri",
        "https://vk.com/neo_kitty_art",
    ]
