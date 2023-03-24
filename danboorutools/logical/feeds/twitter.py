from pathlib import Path

from danboorutools import logger
from danboorutools.logical.progress_tracker import ProgressTracker
from danboorutools.logical.sessions.twitter import TwitterSession
from danboorutools.logical.urls.twitter import TwitterPostUrl
from danboorutools.models.feed import Feed
from danboorutools.models.has_posts import EndScan


class TwitterFeed(Feed):
    session = TwitterSession()

    def _extract_from_generic(self) -> None:
        following_list: list[int] = list(set(self.session.api.GetFriendIDs(total_count=None)))

        with Path("data/twitter_follows_backup.txt").open("w+", encoding="utf-8") as backup_file:
            backup_file.write("\n".join(map(str, following_list)))  # in case I get banned, fuck twitter

        last_scanned_ids_data: ProgressTracker[dict[int, int]] = ProgressTracker("twitter_feed_last_ids", {})
        last_scanned_ids = last_scanned_ids_data.value
        for index, user_id in enumerate(following_list):
            total = len(following_list)
            pad = len(str(total))

            if last_id := last_scanned_ids.get(user_id, 0):
                logger.info(f"Scanning artist <c>{user_id}</> ({index + 1:>{pad}} of {total}), since id {last_id}.")
            else:
                logger.info(f"Scanning artist <c>{user_id}</> ({index + 1:>{pad}} of {total}) for the first time.")

            user_last_id = self._extract_from_each_artist(user_id, last_id)
            last_scanned_ids[user_id] = user_last_id

        last_scanned_ids_data.value = last_scanned_ids

    def _extract_from_each_artist(self, artist_id: int, last_scanned_id: int) -> int:
        max_id = 0
        previous_max_id = None

        while True:
            tweets = self.session.get_user_tweets(user_id=artist_id, since_id=last_scanned_id, max_id=previous_max_id)
            if not tweets:
                return max_id

            previous_max_id = min(tweets, key=lambda x: x.id).id - 1
            max_id = max(max_id, *[tweet.id for tweet in tweets])

            for tweet in tweets:
                if not tweet.asset_urls:
                    continue

                post = TwitterPostUrl.build(TwitterPostUrl, username=tweet.user.screen_name, post_id=tweet.id)

                try:
                    self._register_post(
                        post=post,
                        assets=tweet.asset_urls,
                        created_at=tweet.created_at,
                        score=tweet.favorite_count or 0,
                    )
                except EndScan:
                    return max_id

                if not last_scanned_id:
                    return max_id

            if not last_scanned_id:
                # needed here too because the loop above might never reach the return if no tweet has media
                return max_id
