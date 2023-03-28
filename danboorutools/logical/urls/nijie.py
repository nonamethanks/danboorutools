import re
from datetime import datetime
from functools import cached_property
from urllib.parse import urljoin

from danboorutools.logical.sessions.nijie import NijieSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.time import datetime_from_string


class NijieUrl(Url):
    session = NijieSession()


class NijiePostUrl(PostUrl, NijieUrl):
    post_id: int

    normalize_template = "https://nijie.info/view.php?id={post_id}"

    @cached_property
    def score(self) -> int:
        return self.html.select_one("#good_cnt").text

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
        other_images = other_images_container.select("img.mozamoza.ngtag")

        return [urljoin("https://", img["src"]) for img in [main_image, *other_images]]


class NijieArtistUrl(ArtistUrl, NijieUrl):
    user_id: int

    normalize_template = "https://nijie.info/members.php?id={user_id}"


class NijieImageUrl(PostAssetUrl, NijieUrl):
    page: int | None  # starts from 0
    post_id: int | None
    user_id: int | None

    def parse_filename(self, filename: str) -> None:
        filename_parts = filename.split(".")[0].split("_")
        if len(filename_parts) == 1:
            # 20120615025744927.jpg
            self.user_id = None
            self.page = None
            self.post_id = None
        if len(filename_parts) == 2 and len(filename_parts[1]) == 14:
            # 28310_20131101215959.jpg
            self.user_id = int(filename_parts[0])
            self.page = 0
            self.post_id = None
        elif len(filename_parts) == 3 and len(filename_parts[1]) == 14:
            # 236014_20170620101426_0.png
            # 829001_20190620004513_0.mp4
            # 559053_20180604023346_1.png
            self.post_id = None
            [self.user_id, _, self.page] = map(int, filename_parts)
        elif len(filename_parts) == 4 and filename_parts[2].isnumeric() and filename_parts[3].isnumeric():
            # 287736_161475_20181112032855_1.png
            if len(filename_parts[2]) == 14:
                [self.post_id, self.user_id, _, self.page] = map(int, filename_parts)
            # 218856_0_236014_20170620101329.png
            elif len(filename_parts[3]) == 14:
                [self.post_id, _, self.user_id, self.page] = map(int, filename_parts)
        elif len(filename_parts) == 4:
            # 0_0_403fdd541191110c_c25585.jpg
            # 218856_1_7646cf57f6f1c695_f2ed81.png
            self.post_id = int(filename_parts[0]) if filename_parts[0] != "0" else None
            self.page = int(filename_parts[1])
            self.user_id = None

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
