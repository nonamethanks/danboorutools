from collections.abc import Iterator
from itertools import repeat

from danboorutools.logical.sessions.patreon import PatreonCampaignPostData, PatreonSession
from danboorutools.logical.urls.patreon import _process_post
from danboorutools.models.feed import Feed


class PatreonFeed(Feed):
    session = PatreonSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[tuple[PatreonCampaignPostData, list[dict]]]]:  # fucking patreon
        cursor = None
#
        while True:
            page_results = self.session.get_feed(cursor)
            if not page_results.data:
                return

            yield list(zip(page_results.data, repeat(page_results.included)))
#
            cursor = page_results.data[-1].attributes.published_at.isoformat()
#
    _process_post = _process_post

    @property
    def normalized_url(self) -> str:
        return "https://www.patreon.com/home"
