import pytest

from danboorutools.logical.urls import booth as b
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    b.BoothArtistUrl: {
        "https://re-face.booth.pm/": "https://re-face.booth.pm",
        "https://re-face.booth.pm/items": "https://re-face.booth.pm",
    },
    b.BoothImageUrl: {
        "https://s2.booth.pm/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c_base_resized.jpg": "",
        "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5_base_resized.jpg": "",
        "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.png": "",
        "https://booth.pximg.net/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg": "",
        "https://booth.pximg.net/c/300x300_a2_g5/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg": "",
        "https://booth.pximg.net/c/72x72_a2_g5/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg": "",
        "https://booth.pximg.net/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d.jpeg": "",
        "https://booth.pximg.net/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c.jpg": "",
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
        "https://s2.booth.pm/611c108e-1738-4ac6-965a-4d84243d8a3e/386122a4-29b1-4fbc-8887-ac262c12379a.png": "",
        "https://s.booth.pm/548e2f12-31e4-4553-85b0-be309aaa7310/079b78c1-210c-4b8f-b5ba-5d94c5739bab.jpg?1411739802": "",
        "https://booth.pximg.net/c/128x128/users/3193929/icon_image/5be9eff4-1d9e-4a79-b097-33c1cd4ad314_base_resized.jpg": "",
        "https://booth.pximg.net/users/3193929/icon_image/5be9eff4-1d9e-4a79-b097-33c1cd4ad314.png": "",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://synindx-73train.booth.pm",
        url_type=b.BoothArtistUrl,
        url_properties=dict(username="synindx-73train"),
        primary_names=["とりでぽっぽ"],
        secondary_names=["synindx-73train"],
        related=["https://skeb.jp/@synindx_73train", "https://twitter.com/synindx_73train", "https://www.pixiv.net/en/users/13678408"],
    )


def test_artist_url_2():  # another type of links
    generate_artist_test(
        url_string="https://harawatamgmg.booth.pm/",
        url_type=b.BoothArtistUrl,
        url_properties=dict(username="harawatamgmg"),
        primary_names=["wata"],
        secondary_names=["harawatamgmg"],
        related=["https://www.pixiv.net/users/1337738"],
    )


def test_artist_url_3():  # another type of name element
    generate_artist_test(
        url_string="https://awayukidouhu.booth.pm/",
        url_type=b.BoothArtistUrl,
        url_properties=dict(username="awayukidouhu"),
        primary_names=["BAR 泡雪豆腐"],
        secondary_names=["awayukidouhu"],
        related=["https://www.pixiv.net/users/1772501", "https://twitter.com/kinugoshispark"],
    )


def test_artist_url_4():  # private
    generate_artist_test(
        url_string="https://oriruriro.booth.pm/",
        url_type=b.BoothArtistUrl,
        url_properties=dict(username="oriruriro"),
        primary_names=[],
        secondary_names=["oriruriro"],
        related=[],
    )
