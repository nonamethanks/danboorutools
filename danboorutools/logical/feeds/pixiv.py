from danboorutools.logical.sessions.pixiv import PixivSession
from danboorutools.logical.urls.pixiv import _process_json_post
from danboorutools.models.feed import JsonFeed


class PixivFeed(JsonFeed):
    session = PixivSession()

    posts_json_url = "https://www.pixiv.net/touch/ajax/follow/latest?type=illusts&include_meta=0&p={page}&lang=en"
    posts_objects_dig = ["body", "illusts"]

    _process_json_post = _process_json_post
