

from ward import test

from danboorutools.models.url import Url

urls = {
    "https://www.furaffinity.net/gallery/iwbitu": "https://www.furaffinity.net/user/iwbitu",
    "https://www.furaffinity.net/scraps/iwbitu/2/?": "https://www.furaffinity.net/user/iwbitu",
    "https://www.furaffinity.net/gallery/iwbitu/folder/133763/Regular-commissions": "https://www.furaffinity.net/user/iwbitu",
    "https://www.furaffinity.net/user/lottieloveart/user?user_id=1021820442510802945": "https://www.furaffinity.net/user/lottieloveart",
    "https://www.furaffinity.net/stats/duskmoor/submissions/": "https://www.furaffinity.net/user/duskmoor",

    "https://d.furaffinity.net/art/iwbitu/1650222955/1650222955.iwbitu_yubi.jpg": "https://d.furaffinity.net/art/iwbitu/1650222955/1650222955.iwbitu_yubi.jpg",
    # "https://t.furaffinity.net/46821705@800-1650222955.jpg": "https://t.furaffinity.net/46821705@800-1650222955.jpg",

    "https://a.furaffinity.net/1550854991/iwbitu.gif": "https://a.furaffinity.net/1550854991/iwbitu.gif",

    "https://www.furaffinity.net/view/46821705/": "https://www.furaffinity.net/view/46821705",
    "https://www.furaffinity.net/view/46802202/": "https://www.furaffinity.net/view/46802202",
    "https://www.furaffinity.net/full/46821705/": "https://www.furaffinity.net/view/46821705",
}

for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
