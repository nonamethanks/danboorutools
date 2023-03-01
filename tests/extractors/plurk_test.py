from ward import test

from danboorutools.models.url import Url

urls = {
    "https://www.plurk.com/m/redeyehare": "https://www.plurk.com/redeyehare",
    "https://www.plurk.com/u/ddks2923": "https://www.plurk.com/ddks2923",
    "https://www.plurk.com/m/u/leiy1225": "https://www.plurk.com/leiy1225",
    "https://www.plurk.com/s/u/salmonroe13": "https://www.plurk.com/salmonroe13",
    "https://www.plurk.com/redeyehare": "https://www.plurk.com/redeyehare",
    "https://www.plurk.com/RSSSww/invite/4": "https://www.plurk.com/RSSSww",

    "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg": "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg",
    "https://images.plurk.com/mx_5wj6WD0r6y4rLN0DL3sqag.jpg": "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg",

    "https://www.plurk.com/p/om6zv4": "https://www.plurk.com/p/om6zv4",
    "https://www.plurk.com/m/p/okxzae": "https://www.plurk.com/p/okxzae",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
