import pytest

from danboorutools.logical.urls.hentai_foundry import (
    HentaiFoundryArtistUrl,
    HentaiFoundryImageUrl,
    HentaiFoundryOldPostUrl,
    HentaiFoundryPostUrl,
)
from tests.helpers.parsing import generate_parsing_test

urls = {
    HentaiFoundryArtistUrl: {
        "https://www.hentai-foundry.com/user/kajinman": "https://www.hentai-foundry.com/user/kajinman",
        "https://www.hentai-foundry.com/user/kajinman/profile": "https://www.hentai-foundry.com/user/kajinman",
        "https://www.hentai-foundry.com/user/J-likes-to-draw/profile": "https://www.hentai-foundry.com/user/J-likes-to-draw",


        "https://www.hentai-foundry.com/pictures/user/kajinman": "https://www.hentai-foundry.com/user/kajinman",
        "https://www.hentai-foundry.com/pictures/user/kajinman/scraps": "https://www.hentai-foundry.com/user/kajinman",

        "http://www.hentai-foundry.com/user-RockCandy.php": "https://www.hentai-foundry.com/user/RockCandy",
        "http://www.hentai-foundry.com/profile-sawao.php": "https://www.hentai-foundry.com/user/sawao",
    },
    HentaiFoundryImageUrl: {

        "https://pictures.hentai-foundry.com/a/Afrobull/795025/Afrobull-795025-kuroeda.png": "https://pictures.hentai-foundry.com/a/Afrobull/795025/Afrobull-795025-kuroeda.png",
        "https://pictures.hentai-foundry.com/_/-MadKaiser-/532792/-MadKaiser--532792-FFXIV_Miqote.png": "https://pictures.hentai-foundry.com/_/-MadKaiser-/532792/-MadKaiser--532792-FFXIV_Miqote.png",

        "http://pictures.hentai-foundry.com//s/soranamae/363663.jpg": "http://pictures.hentai-foundry.com//s/soranamae/363663.jpg",
        "http://www.hentai-foundry.com/piccies/d/dmitrys/1183.jpg": "http://www.hentai-foundry.com/piccies/d/dmitrys/1183.jpg",

    },
    HentaiFoundryPostUrl: {
        "https://www.hentai-foundry.com/pictures/user/Afrobull/795025": "https://www.hentai-foundry.com/pictures/user/Afrobull/795025",
        "https://www.hentai-foundry.com/pictures/user/Afrobull/795025/kuroeda": "https://www.hentai-foundry.com/pictures/user/Afrobull/795025",

    },
    HentaiFoundryOldPostUrl: {
        "https://thumbs.hentai-foundry.com/thumb.php?pid=795025&size=350": "https://www.hentai-foundry.com/pic-795025",
        "http://www.hentai-foundry.com/pic-795025": "https://www.hentai-foundry.com/pic-795025",
        "http://www.hentai-foundry.com/pic-149160.html": "https://www.hentai-foundry.com/pic-149160",
        "http://www.hentai-foundry.com/pic-149160.php": "https://www.hentai-foundry.com/pic-149160",
        "http://www.hentai-foundry.com/pic_full-66045.php": "https://www.hentai-foundry.com/pic-66045",
        "http://www.hentai-foundry.com/pictures/151578/": "https://www.hentai-foundry.com/pic-151578",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
