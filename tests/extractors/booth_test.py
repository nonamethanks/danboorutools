from ward import test

from danboorutools.models.url import Url

urls = {
    "https://re-face.booth.pm/": "https://re-face.booth.pm",
    "https://re-face.booth.pm/items": "https://re-face.booth.pm",
    "https://s2.booth.pm/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c_base_resized.jpg": "https://s2.booth.pm/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c.jpg",
    "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5_base_resized.jpg": "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.jpg",
    "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.png": "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.png",
    "https://re-face.booth.pm/items/3435711": "https://re-face.booth.pm/items/3435711",

    "https://booth.pm/en/items/2864768": "https://booth.pm/items/2864768",
    "https://booth.pm/ja/items/2864768": "https://booth.pm/items/2864768",
    "https://re-face.booth.pm/item_lists/m4ZTWzb8": "https://re-face.booth.pm/item_lists/m4ZTWzb8",

    "https://s2.booth.pm/611c108e-1738-4ac6-965a-4d84243d8a3e/386122a4-29b1-4fbc-8887-ac262c12379a.png": "https://s2.booth.pm/611c108e-1738-4ac6-965a-4d84243d8a3e/386122a4-29b1-4fbc-8887-ac262c12379a.png",
    "https://s.booth.pm/548e2f12-31e4-4553-85b0-be309aaa7310/079b78c1-210c-4b8f-b5ba-5d94c5739bab.jpg?1411739802": "https://s.booth.pm/548e2f12-31e4-4553-85b0-be309aaa7310/079b78c1-210c-4b8f-b5ba-5d94c5739bab.jpg",
}

for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
