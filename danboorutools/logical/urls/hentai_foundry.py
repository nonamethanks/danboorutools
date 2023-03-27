import re
from datetime import datetime
from functools import cached_property

from danboorutools.logical.sessions.hentai_foundry import HentaiFoundrySession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.time import datetime_from_string


class HentaiFoundryUrl(Url):
    session = HentaiFoundrySession()


class HentaiFoundryPostUrl(PostUrl, HentaiFoundryUrl):
    username: str
    post_id: int

    normalize_template = "https://www.hentai-foundry.com/pictures/user/{username}/{post_id}"

    @cached_property
    def created_at(self) -> datetime:
        created_at = self.html.select_one(".boxbody time")["datetime"]
        return datetime_from_string(created_at)

    @cached_property
    def score(self) -> int:
        data = re.findall(r"Views</span>\s*(\d+)\s*<br", str(self.html))
        return int(data[0])

    def _extract_assets(self) -> list[str]:
        image_element = self.html.select_one("img.center")
        if not image_element:
            if self.html.select_one("[type='application/x-shockwave-flash']"):
                return []
            raise NotImplementedError(self)

        return ["https:" + image_element["src"]]


class HentaiFoundryArtistUrl(ArtistUrl, HentaiFoundryUrl):
    username: str

    normalize_template = "https://www.hentai-foundry.com/user/{username}"


class HentaiFoundryImageUrl(PostAssetUrl, HentaiFoundryUrl):
    username: str
    work_id: int

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


class HentaiFoundryOldPostUrl(RedirectUrl, HentaiFoundryUrl):
    post_id: int

    normalize_template = "https://www.hentai-foundry.com/pic-{post_id}"
