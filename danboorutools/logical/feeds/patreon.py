import re
from collections.abc import Iterator
from itertools import repeat

from danboorutools.logical.sessions.patreon import PatreonCampaignPostData, PatreonSession
from danboorutools.logical.urls.patreon import PatreonArtistUrl, PatreonPostUrl
from danboorutools.models.feed import Feed
from danboorutools.models.url import Url


class PatreonFeed(Feed):
    session = PatreonSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[tuple[PatreonCampaignPostData, list[dict]]]]:  # fucking patreon
        cursor = None

        while True:
            page_json = self.session.get_feed(cursor)

            assert page_json.data
            yield list(zip(page_json.data, repeat(page_json.included)))  # noqa: B905

            cursor = page_json.data[-1].attributes.published_at

    def _process_post(self, post_object: tuple[PatreonCampaignPostData, list[dict]]) -> None:
        _post_object, included = post_object
        if not _post_object.attributes.current_user_can_view:
            return

        if not (assets := _post_object.get_assets(included)):
            return

        post_url = _post_object.attributes.patreon_url
        if post_url.startswith("/"):
            post_url = "https://www.patreon.com" + post_url
        post = Url.parse(post_url)
        assert isinstance(post, PatreonPostUrl)

        upgrade_url = _post_object.attributes.upgrade_url
        username_match = re.search(r"\/join\/(\w+)\/checkout", upgrade_url)
        if not username_match:
            raise NotImplementedError
        post.gallery = PatreonArtistUrl.build(PatreonArtistUrl, username=username_match.groups()[0])

        self._register_post(
            post=post,
            assets=assets,
            created_at=_post_object.attributes.published_at,
            score=_post_object.attributes.like_count,
        )
