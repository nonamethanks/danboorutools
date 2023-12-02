import pytest

from danboorutools.logical.urls.linktree import LinktreeUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_info_test

urls = {
    LinktreeUrl: {
        "https://linktr.ee/tyanka6": "https://linktr.ee/tyanka6",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_info_url_1():
    generate_info_test(
        url_string="https://linktr.ee/tyanka6/",
        url_type=LinktreeUrl,
        url_properties=dict(username="tyanka6"),
        primary_names=[],
        secondary_names=["tyanka6"],
        related=[
            "https://t.me/+CbICDRONGN02ZTZi",
            "https://twitter.com/Himetyan_art",
            "https://twitter.com/hime_tyan_art",
            "https://vm.tiktok.com/ZM8W1dq9D/",
            "https://www.artstation.com/himetyan",
            "https://www.deviantart.com/himetyan",
            "https://www.instagram.com/hime_tyan_art",
            "https://www.patreon.com/himetyanart",
            "https://discordapp.com/users/1018473584835964939/",
            "https://www.pixiv.net/en/users/91907481",
            "https://ko-fi.com/himetyanart",
            "https://drive.google.com/file/d/1RkuVu_WGlEmpmholNV-EKD1CcQCR62C1/view?usp=sharing",
        ],
    )
