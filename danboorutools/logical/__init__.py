
from danboorutools.logical.api.danbooru import DanbooruApi  # pylint: disable=wrong-import-position  # noqa
from danboorutools.logical.api.gelbooru import GelbooruApi  # pylint: disable=wrong-import-position  # noqa

# autopep8: on

danbooru_api = DanbooruApi(domain="danbooru", mode="bot")
gelbooru_api = GelbooruApi()
