import pytest

from danboorutools.logical.urls import vk
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test, generate_post_test, generate_redirect_test

urls = {
    vk.VkArtistUrl: {
        "https://vk.com/drinkai": "https://vk.com/drinkai",
        "https://vk.com/amaksart/rocjoker0120": "https://vk.com/amaksart",
    },
    vk.VkArtistIdUrl: {
        "https://vk.com/wall-29240722": "https://vk.com/public29240722",
        "https://vk.com/public219466993": "https://vk.com/public219466993",
    },
    vk.VkPostUrl: {
        "https://vk.com/wall-194021906_2631": "https://vk.com/wall-194021906_2631",
        "https://vk.com/zap_nik_home?w=wall-160278046_16921": "https://vk.com/wall-160278046_16921",
    },
    vk.VkPhotoUrl: {
        "https://vk.com/photo-40794778_457241864": "https://vk.com/photo-40794778_457241864",
        "https://m.vk.com/albums-101241592?z=photo-101241592_457246767%2Fphotos-101241592": "https://vk.com/photo-101241592_457246767",
    },
    vk.VkAlbumUrl: {
        "https://vk.com/album-45929789_165947060": "https://vk.com/album-45929789_165947060",
    },
    vk.VkPostReplyUrl: {
        "https://vk.com/wall-71303622_1375?reply=1376": "https://vk.com/wall-71303622_1375?reply=1376",
    },
    vk.VkFileUrl: {
        "https://vk.com/doc193353135_674199660?hash=q6PUsNW4GRz1H0FP9ZgsQi1zEZech6xAkO4JKlOnjCH&dl=0nrCZFfpjAsdmuEwpkgAXzodJ8yDQJrO89t2kGj90AX": "https://vk.com/doc193353135_674199660",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_post_url_1():
    generate_post_test(
        url_string="https://vk.com/straywhispertaker?z=photo-147565682_457271000%2Falbum-147565682_269415385",
        url_type=vk.VkPhotoUrl,
        url_properties=dict(username="straywhispertaker",
                            album_id="269415385",
                            photo_id="457271000",
                            user_id="147565682"),
    )


def test_artist_url_1():
    generate_artist_test(
        url_string="https://vk.com/drinkai",
        url_type=vk.VkArtistUrl,
        url_properties=dict(username="drinkai"),
        primary_names=["Пьяная Нейросеть"],
        secondary_names=["drinkai"],
        related=[],
    )


def test_redirect_url_1():
    generate_redirect_test(
        url_string="https://vk.com/public219466993",
        url_type=vk.VkArtistIdUrl,
        url_properties=dict(user_id="219466993"),
        redirects_to="https://vk.com/drinkai",
    )
