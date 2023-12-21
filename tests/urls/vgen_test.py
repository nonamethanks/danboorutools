import pytest

from danboorutools.logical.urls.vgen import VgenArtistUrl, VgenPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    VgenArtistUrl: {
        "http://vgen.co/LuluSensei": "https://vgen.co/LuluSensei",
        "https://vgen.co/Umiya/portfolio": "https://vgen.co/Umiya",
    },
    VgenPostUrl: {
        "https://vgen.co/saire/portfolio/showcase/cypher-s-character-illust/3deb91c1-9e45-4242-9c89-53a92047dfea": "https://vgen.co/saire/portfolio/showcase/cypher-s-character-illust/3deb91c1-9e45-4242-9c89-53a92047dfea",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestVgenArtistUrl(_TestArtistUrl):
    url_string = "http://vgen.co/LuluSensei"
    url_type = VgenArtistUrl
    url_properties = dict(username="LuluSensei")
    primary_names = ["LuluSensei"]
    secondary_names = ["LuluSensei"]
    related = ["https://twitter.com/LuluannSensei", "https://www.artstation.com/lulusensei"]
