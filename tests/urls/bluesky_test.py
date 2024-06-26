import pytest

from danboorutools.logical.urls.bluesky import BlueskyArtistUrl, BlueskyImageUrl, BlueskyPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    BlueskyArtistUrl: {
        "https://bsky.app/profile/torizono1024.bsky.social": "https://bsky.app/profile/torizono1024.bsky.social",
        "https://bsky.app/profile/rnarccus.art": "https://bsky.app/profile/rnarccus.art",
        "http://halooge.bsky.social": "https://bsky.app/profile/halooge.bsky.social",

    },
    BlueskyPostUrl: {
        "https://bsky.app/profile/minacream.bsky.social/post/3k6mfqfio4c2b": "https://bsky.app/profile/minacream.bsky.social/post/3k6mfqfio4c2b",
    },
    BlueskyImageUrl: {
        "https://cdn.bsky.app/img/feed_fullsize/plain/did:plc:lw3bmyvvbdp7cvi2xk5s3n2h/bafkreidllzyyiqmsh3pnjftnniovdidl33svzlcih5nnsaickiglojngtq@jpeg": "https://cdn.bsky.app/img/feed_fullsize/plain/did:plc:lw3bmyvvbdp7cvi2xk5s3n2h/bafkreidllzyyiqmsh3pnjftnniovdidl33svzlcih5nnsaickiglojngtq",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestBlueskyArtistUrl(_TestArtistUrl):
    url_string = "https://bsky.app/profile/windmill-g.bsky.social"
    url_type = BlueskyArtistUrl
    url_properties = dict(username="windmill-g.bsky.social")
    primary_names = ["Windmill 🔞"]
    secondary_names = ["windmill-g"]
    related = ["https://linktr.ee/windmillg"]
