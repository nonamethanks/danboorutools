from danboorutools.logical.sessions.pixiv import PixivSession
from danboorutools.logical.urls.pixiv import _process_post_from_json
from danboorutools.models.feed import Feed


class PixivFeed(Feed):
    session = PixivSession()

    posts_json_url = "https://www.pixiv.net/touch/ajax/follow/latest?type=illusts&include_meta=0&p={page}&lang=en"
    posts_objects_dig = ["body", "illusts"]

    _process_post_from_json = _process_post_from_json
