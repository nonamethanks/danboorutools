import pytest

from danboorutools.logical.urls.artstation import (
    ArtStationArtistUrl,
    ArtStationImageUrl,
    ArtStationMarketplacePostUrl,
    ArtStationOldPostUrl,
    ArtStationPostUrl,
)
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    ArtStationOldPostUrl: {
        "https://www.artstation.com/artwork/cody-from-sf": "https://www.artstation.com/artwork/cody-from-sf",
    },
    ArtStationPostUrl: {
        "https://www.artstation.com/artwork/04XA4": "https://www.artstation.com/artwork/04XA4",
        "https://sa-dui.artstation.com/projects/DVERn": "https://sa-dui.artstation.com/projects/DVERn",
        "https://dudeunderscore.artstation.com/projects/NoNmD?album_id=23041": "https://dudeunderscore.artstation.com/projects/NoNmD",
    },
    ArtStationArtistUrl: {
        "https://artstation.com/artist/sa-dui": "https://www.artstation.com/sa-dui",
        "https://www.artstation.com/artist/chicle/albums/all/": "https://www.artstation.com/chicle",
        "https://www.artstation.com/artist/sa-dui": "https://www.artstation.com/sa-dui",

        "http://www.artstation.com/envie_dai/prints": "https://www.artstation.com/envie_dai",
        "https://www.artstation.com/chicle/albums/all": "https://www.artstation.com/chicle",
        "https://www.artstation.com/felipecartin/profile": "https://www.artstation.com/felipecartin",
        "https://www.artstation.com/h-battousai/albums/1480261": "https://www.artstation.com/h-battousai",
        "https://www.artstation.com/sa-dui": "https://www.artstation.com/sa-dui",

        "https://heyjay.artstation.com/store/art_posters": "https://www.artstation.com/heyjay",
        "https://hosi_na.artstation.com": "https://www.artstation.com/hosi_na",
        "https://sa-dui.artstation.com": "https://www.artstation.com/sa-dui",
        "https://sa-dui.artstation.com/projects": "https://www.artstation.com/sa-dui",
    },
    ArtStationImageUrl: {

        "https://cdna.artstation.com/p/assets/images/images/005/804/224/large/titapa-khemakavat-sa-dui-srevere.jpg?1493887236": "https://cdn.artstation.com/p/assets/images/images/005/804/224/4k/titapa-khemakavat-sa-dui-srevere.jpg",
        "https://cdnb.artstation.com/p/assets/images/images/014/410/217/smaller_square/bart-osz-bartosz1812041.jpg?1543866276": "https://cdn.artstation.com/p/assets/images/images/014/410/217/4k/bart-osz-bartosz1812041.jpg",
        "https://cdna.artstation.com/p/assets/images/images/007/253/680/4k/ina-wong-demon-girl-done-ttd-comp.jpg?1504793833": "https://cdn.artstation.com/p/assets/images/images/007/253/680/4k/ina-wong-demon-girl-done-ttd-comp.jpg",
        "https://cdna.artstation.com/p/assets/covers/images/007/262/828/small/monica-kyrie-1.jpg?1504865060": "https://cdn.artstation.com/p/assets/covers/images/007/262/828/4k/monica-kyrie-1.jpg",

        "https://cdn-animation.artstation.com/p/video_sources/000/466/622/workout.mp4": "https://cdn-animation.artstation.com/p/video_sources/000/466/622/workout.mp4",

    },
    ArtStationMarketplacePostUrl: {
        "https://www.artstation.com/marketplace/p/X9P5": "https://www.artstation.com/marketplace/p/X9P5",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestArtStationArtistUrl(_TestArtistUrl):
    url_string = "https://himetyan.artstation.com/"
    url_type = ArtStationArtistUrl
    url_properties = dict(username="himetyan")
    primary_names = ["Hime tyan art"]
    secondary_names = ["himetyan"]
    related = ["https://www.instagram.com/hime_tyan_art"]
