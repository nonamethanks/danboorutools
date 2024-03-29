import re
from datetime import datetime
from functools import cached_property
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from danboorutools.logical.sessions.nijie import NijieSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url, _AssetUrl
from danboorutools.util.time import datetime_from_string


class NijieUrl(Url):
    session = NijieSession()

    @cached_property
    def html(self) -> BeautifulSoup:
        if not isinstance(self, _AssetUrl):
            self.session.login()
        return super().html


class NijiePostUrl(PostUrl, NijieUrl):
    post_id: int

    normalize_template = "https://nijie.info/view.php?id={post_id}"

    @cached_property
    def score(self) -> int:
        assert (score_el := self.html.select_one("#good_cnt"))
        return int(score_el.text.strip())

    @cached_property
    def created_at(self) -> datetime:
        timestamp_match = re.search(r"投稿時間：(?P<time>[\w\-: ]+)", str(self.html))
        timestamp_match = timestamp_match or re.search(r"投稿日:\s<span>(?P<time>[\w\-: ]+)</span>", str(self.html))
        if not timestamp_match:
            raise NotImplementedError(self)

        timestamp = timestamp_match.groupdict()["time"].strip()
        return datetime_from_string(timestamp, backup_tz="Asia/Tokyo")

    def _extract_assets(self) -> list[str]:
        if self.html.select_one("#dojin_left"):
            main_image = self.html.select_one("#dojin_left .left img")
            other_images_container = self.html.select_one("div#dojin_diff")

        elif self.html.select_one("#view-center"):
            main_image = self.html.select_one("#img_filter img.ngtag")
            other_images_container = self.html.select_one("div#img_diff")
        else:
            raise NotImplementedError(self)

        assert main_image, self
        assert other_images_container
        other_images = other_images_container.select("img.mozamoza.ngtag")

        return [urljoin("https://", img["src"]) for img in [main_image, *other_images]]


class NijieArtistUrl(ArtistUrl, NijieUrl):
    user_id: int

    normalize_template = "https://nijie.info/members.php?id={user_id}"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one("#main-left .name"))
        return [name_el.text]

    @property
    def secondary_names(self) -> list[str]:
        return [f"nijie_{self.user_id}"]

    @property
    def related(self) -> list[Url]:
        assert (url_els := self.html.select("#main-center-none #prof a:not(.__cf_email__)"))
        return list(map(Url.parse, [u.text for u in url_els]))


class NijieImageUrl(PostAssetUrl, NijieUrl):
    page: int | None  # starts from 0
    post_id: int | None
    user_id: int | None

    @staticmethod
    def parse_filename(filename: str) -> tuple[int | None, int | None, int | None]:
        filename_parts = filename.split(".")[0].split("_")
        if len(filename_parts) == 1:
            # 20120615025744927.jpg
            user_id = None
            page = None
            post_id = None
        elif len(filename_parts) == 2 and len(filename_parts[1]) == 14:
            # 28310_20131101215959.jpg
            user_id = int(filename_parts[0])
            page = 0
            post_id = None
        elif len(filename_parts) == 3 and len(filename_parts[1]) == 14:
            # 236014_20170620101426_0.png
            # 829001_20190620004513_0.mp4
            # 559053_20180604023346_1.png
            post_id = None
            [user_id, _, page] = map(int, filename_parts)
        elif len(filename_parts) == 4 and filename_parts[2].isnumeric() and filename_parts[3].isnumeric():
            # 287736_161475_20181112032855_1.png
            if len(filename_parts[2]) == 14:
                [post_id, user_id, _, page] = map(int, filename_parts)
            # 218856_0_236014_20170620101329.png
            elif len(filename_parts[3]) == 14:
                [post_id, _, user_id, page] = map(int, filename_parts)
            else:
                raise NotImplementedError
        elif len(filename_parts) == 4:
            # 0_0_403fdd541191110c_c25585.jpg
            # 218856_1_7646cf57f6f1c695_f2ed81.png
            post_id = int(filename_parts[0]) if filename_parts[0] != "0" else None
            page = int(filename_parts[1])
            user_id = None
        else:
            raise NotImplementedError

        return post_id, page, user_id

    @ property
    def full_size(self) -> str:
        if self.parsed_url.url_parts[-1] == "view_popup.php":
            if self.post_id is None or self.page is None:
                raise NotImplementedError(self.parsed_url.raw_url)
            if self.page:
                return f"https://nijie.info/view_popup.php?id={self.post_id}#diff_{self.page}"
            else:
                return f"https://nijie.info/view_popup.php?id={self.post_id}"
        else:
            return re.sub(r"__rs_\w+/", "", self.parsed_url.raw_url).replace("http:", "https:")
