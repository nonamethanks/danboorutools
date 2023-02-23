

# pylint: disable=cell-var-from-loop
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://www.artstation.com/artwork/cody-from-sf": "https://www.artstation.com/artwork/cody-from-sf",

    "https://www.artstation.com/artwork/04XA4": "https://www.artstation.com/artwork/04XA4",
    "https://sa-dui.artstation.com/projects/DVERn": "https://sa-dui.artstation.com/projects/DVERn",
    "https://dudeunderscore.artstation.com/projects/NoNmD?album_id=23041": "https://dudeunderscore.artstation.com/projects/NoNmD",

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

    "https://cdna.artstation.com/p/assets/images/images/005/804/224/large/titapa-khemakavat-sa-dui-srevere.jpg?1493887236": "https://cdn.artstation.com/p/assets/images/images/005/804/224/4k/titapa-khemakavat-sa-dui-srevere.jpg",
    "https://cdnb.artstation.com/p/assets/images/images/014/410/217/smaller_square/bart-osz-bartosz1812041.jpg?1543866276": "https://cdn.artstation.com/p/assets/images/images/014/410/217/4k/bart-osz-bartosz1812041.jpg",
    "https://cdna.artstation.com/p/assets/images/images/007/253/680/4k/ina-wong-demon-girl-done-ttd-comp.jpg?1504793833": "https://cdn.artstation.com/p/assets/images/images/007/253/680/4k/ina-wong-demon-girl-done-ttd-comp.jpg",
    "https://cdna.artstation.com/p/assets/covers/images/007/262/828/small/monica-kyrie-1.jpg?1504865060": "https://cdn.artstation.com/p/assets/covers/images/007/262/828/4k/monica-kyrie-1.jpg",

    "https://cdn-animation.artstation.com/p/video_sources/000/466/622/workout.mp4": "https://cdn-animation.artstation.com/p/video_sources/000/466/622/workout.mp4",

    "https://www.artstation.com/marketplace/p/X9P5": "https://www.artstation.com/marketplace/p/X9P5",

}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
