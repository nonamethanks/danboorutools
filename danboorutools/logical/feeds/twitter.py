from collections.abc import Iterator

from danboorutools import logger
from danboorutools.logical.sessions.twitter import TwitterSession, TwitterTimelineTweetData
from danboorutools.logical.urls.twitter import TwitterPostUrl
from danboorutools.models.feed import Feed


class TwitterFeed(Feed):
    session = TwitterSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[TwitterTimelineTweetData]]:

        cursor = None
        self.last_id = int(self.last_id) if self.last_id else None
        if self.last_id:
            logger.info(f"Getting all IDs > {self.last_id}")
            old_last_id = self.last_id
        else:
            old_last_id = 0

        while True:
            result = self.session.get_feed(cursor=cursor)

            if old_last_id:
                new_tweets = [t for t in result.tweets if int(t.id_str) > old_last_id]
                logger.info(f"{len(new_tweets)} tweets out of {len(result.tweets)} retrieved have ID > {old_last_id}.")
            else:
                new_tweets = result.tweets

            self.last_id = max(self.last_id or 0, *[int(t.id_str) for t in result.tweets])
            if not new_tweets:
                logger.info(f"No ID found > {old_last_id}")
                return

            yield new_tweets
            if not result.next_cursor:
                logger.info("No next cursor returned. Quitting...")
                return
            cursor = result.next_cursor

    def _process_post(self, post_object: TwitterTimelineTweetData) -> None:
        if not post_object.assets:
            return

        if post_object.retweeted_status_result:
            if post_object.retweeted_status_result.get("result"):
                return
            else:
                raise NotImplementedError(post_object.retweeted_status_result)

        url = TwitterPostUrl.parse_and_assert(post_object.entities["media"][0]["expanded_url"])
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
