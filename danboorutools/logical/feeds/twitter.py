from collections.abc import Iterator

from danboorutools.logical.sessions.twitter import TwitterSession, TwitterTimelineTweetData
from danboorutools.logical.urls.twitter import TwitterPostUrl
from danboorutools.models.feed import Feed


class TwitterFeed(Feed):
    session = TwitterSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[TwitterTimelineTweetData]]:
        cursor = None
        while True:
            result = self.session.get_feed(cursor=cursor)
            yield result.tweets
            if not result.next_cursor:
                return
            cursor = result.next_cursor

    def _process_post(self, post_object: TwitterTimelineTweetData) -> None:
        if not post_object.assets:
            return

        url = TwitterPostUrl.parse(post_object.entities["media"][0]["expanded_url"])
        assert isinstance(url, TwitterPostUrl)
        username = url.username

        self._register_post(
            post=TwitterPostUrl.build(username=username, post_id=post_object.id_str),
            assets=post_object.assets,
            score=post_object.favorite_count,
            created_at=post_object.created_at,
        )

    @property
    def normalized_url(self) -> str:
        return "https://twitter.com/home"
