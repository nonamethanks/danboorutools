import os
from functools import cached_property

import twitter

from danboorutools.exceptions import UrlIsDeleted
from danboorutools.logical.sessions import Session
from danboorutools.util.misc import memoize


class TwitterSession(Session):

    @cached_property
    def api(self) -> twitter.Api:
        consumer_key = os.environ["TWITTER_CONSUMER_KEY"]
        consumer_secret = os.environ["TWITTER_CONSUMER_KEY_SECRET"]
        access_token = os.environ["TWITTER_ACCESS_TOKEN"]
        access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

        return twitter.Api(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            sleep_on_rate_limit=True,
            tweet_mode="extended"
        )

    @memoize
    def user_data(self, username: str | None = None, user_id: int | None = None) -> dict:
        assert username or user_id
        try:
            return self.api.GetUser(screen_name=username, user_id=user_id, return_json=True, include_entities=True)
        except twitter.error.TwitterError as e:
            if "User not found." in str(e) or "User has been suspended." in str(e):
                original_url = f"https://twitter.com/{username}" if username else f"https://twitter.com/intent/user?user_id={user_id}"
                raise UrlIsDeleted(status_code=404, original_url=original_url) from e
            raise
