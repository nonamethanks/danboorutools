from danboorutools.logical.urls import booth as b
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    b.BoothArtistUrl: {
        "https://re-face.booth.pm/": "https://re-face.booth.pm",
        "https://re-face.booth.pm/items": "https://re-face.booth.pm",
    },
    b.BoothImageUrl: {
        "https://s2.booth.pm/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c_base_resized.jpg": "https://s2.booth.pm/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c.jpg",
        "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5_base_resized.jpg": "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.jpg",
        "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.png": "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.png",

    },
    b.BoothItemUrl: {
        "https://re-face.booth.pm/items/3435711": "https://re-face.booth.pm/items/3435711",

        "https://booth.pm/en/items/2864768": "https://booth.pm/items/2864768",
        "https://booth.pm/ja/items/2864768": "https://booth.pm/items/2864768",
    },
    b.BoothItemListUrl: {
        "https://re-face.booth.pm/item_lists/m4ZTWzb8": "https://re-face.booth.pm/item_lists/m4ZTWzb8",
    },
    b.BoothProfileImageUrl: {
        "https://s2.booth.pm/611c108e-1738-4ac6-965a-4d84243d8a3e/386122a4-29b1-4fbc-8887-ac262c12379a.png": "https://s2.booth.pm/611c108e-1738-4ac6-965a-4d84243d8a3e/386122a4-29b1-4fbc-8887-ac262c12379a.png",
        "https://s.booth.pm/548e2f12-31e4-4553-85b0-be309aaa7310/079b78c1-210c-4b8f-b5ba-5d94c5739bab.jpg?1411739802": "https://s.booth.pm/548e2f12-31e4-4553-85b0-be309aaa7310/079b78c1-210c-4b8f-b5ba-5d94c5739bab.jpg",
    },
}

generate_parsing_suite(urls)

assert_artist_url(
    "https://synindx-73train.booth.pm",
    b.BoothArtistUrl,
    url_properties=dict(username="synindx-73train"),
    primary_names=["とりでぽっぽ"],
    secondary_names=["synindx-73train"],
    related=["https://skeb.jp/@synindx_73train", "https://twitter.com/synindx_73train", "https://www.pixiv.net/en/users/13678408"],
)

assert_artist_url(  # another type of links
    "https://harawatamgmg.booth.pm/",
    b.BoothArtistUrl,
    url_properties=dict(username="harawatamgmg"),
    primary_names=["wata"],
    secondary_names=["harawatamgmg"],
    related=["https://www.pixiv.net/users/1337738"],
)

assert_artist_url(  # private
    "https://oriruriro.booth.pm/",
    b.BoothArtistUrl,
    url_properties=dict(username="oriruriro"),
    primary_names=[],
    secondary_names=["oriruriro"],
    related=[],
)
