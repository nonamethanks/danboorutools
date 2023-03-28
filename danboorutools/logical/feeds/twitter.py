from collections.abc import Iterator
from pathlib import Path

from danboorutools.logical.progress_tracker import ProgressTracker
from danboorutools.logical.sessions.twitter import TwitterSession, TwitterTweetData
from danboorutools.logical.urls.twitter import TwitterPostUrl
from danboorutools.models.feed import FeedWithSeparateArtists


class TwitterFeed(FeedWithSeparateArtists):
    session = TwitterSession()
    previous_max_ids = ProgressTracker[dict[int, int]]("twitter_feed_last_ids", {}).value

    def _extract_artists(self) -> list[int]:
        following_list: list[int] = list(set(self.session.api.GetFriendIDs(total_count=None)))

        with Path("data/twitter_follows_backup.txt").open("w+", encoding="utf-8") as backup_file:
            backup_file.write("\n".join(map(str, following_list)))  # in case I get banned, fuck twitter

        return following_list

    def _extract_posts_from_each_artist(self, artist: int) -> Iterator[list[TwitterTweetData]]:
        previously_found_max_id = self.previous_max_ids.get(artist, 0)
        current_max_id_found = 0
        current_min_id_found = 0

        while True:
            tweets = self.session.get_user_tweets(
                user_id=artist,
                max_id=current_min_id_found,
                since_id=previously_found_max_id,
            )

            if not tweets:
                return

            current_max_id_found = max(tweets, key=lambda x: x.id).id
            current_min_id_found = min(tweets, key=lambda x: x.id).id

            if current_max_id_found < self.previous_max_ids.get(artist, 0):
                self.previous_max_ids[artist] = current_max_id_found

            yield tweets

    def _post_scan_hook(self) -> None:
        ProgressTracker[dict[int, int]]("twitter_feed_previous_max_ids", {}).value = self.previous_max_ids

    def _process_post(self, post_object: TwitterTweetData) -> None:
        if not post_object.asset_urls:
            return

        post = TwitterPostUrl.build(TwitterPostUrl, username=post_object.user.screen_name, post_id=post_object.id)

        self._register_post(
            post=post,
            assets=post_object.asset_urls,
            created_at=post_object.created_at,
            score=post_object.favorite_count or 0,
        )
