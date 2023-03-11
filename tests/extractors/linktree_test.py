from danboorutools.logical.extractors.linktree import LinktreeUrl
from tests.extractors import assert_info_url, generate_parsing_suite

urls = {
    LinktreeUrl: {
        "https://linktr.ee/tyanka6": "https://linktr.ee/tyanka6",
    },
}

generate_parsing_suite(urls)

assert_info_url(
    "https://linktr.ee/tyanka6/",
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
        "https://www.fiverr.com/s2/3d04bb16ba",
        "https://www.instagram.com/hime_tyan_art",
        "https://www.patreon.com/himetyanart",
    ],
)
