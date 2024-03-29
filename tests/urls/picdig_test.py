import pytest

from danboorutools.logical.urls.picdig import PicdigArtistImageUrl, PicdigArtistUrl, PicdigImageUrl, PicdigPostUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    PicdigArtistUrl: {
        "https://picdig.net/supercanoyan/portfolio": "https://picdig.net/supercanoyan",
        "https://picdig.net/supercanoyan/profile": "https://picdig.net/supercanoyan",
        "https://picdig.net/supercanoyan/collections": "https://picdig.net/supercanoyan",
        "https://picdig.net/supercanoyan/articles": "https://picdig.net/supercanoyan",
    },
    PicdigImageUrl: {
        "https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/54e476f5-f956-497d-b689-0db7e745907d/2021/12/b35f9c35-a37f-47b0-a5b6-e639a4535ce3.jpg": "https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/54e476f5-f956-497d-b689-0db7e745907d/2021/12/b35f9c35-a37f-47b0-a5b6-e639a4535ce3.jpg",
        "https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/54e476f5-f956-497d-b689-0db7e745907d/2021/12/63fffa1f-2862-4aa6-80dc-b5a73d91ab43.png": "https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/54e476f5-f956-497d-b689-0db7e745907d/2021/12/63fffa1f-2862-4aa6-80dc-b5a73d91ab43.png",

    },
    PicdigPostUrl: {
        "https://picdig.net/supercanoyan/projects/71c55605-3eca-4660-991c-ee24b9a7b684": "https://picdig.net/supercanoyan/projects/71c55605-3eca-4660-991c-ee24b9a7b684",
    },
    PicdigArtistImageUrl: {
        "https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/2021/12/9fadd3f4-c131-4f26-bce5-26c9d5bd4927.jpg": "https://picdig.net/images/98a85315-ade6-42c7-b54a-a1ab7dc0c7da/2021/12/9fadd3f4-c131-4f26-bce5-26c9d5bd4927.jpg",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
