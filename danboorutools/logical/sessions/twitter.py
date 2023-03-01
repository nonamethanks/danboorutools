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
    def user_data(self, username: str) -> dict:
        try:
            return self.api.GetUser(screen_name=username, return_json=True, include_entities=True)
        except twitter.error.TwitterError as e:
            if "User not found." in str(e) or "User has been suspended." in str(e):
                raise UrlIsDeleted(status_code=404, original_url=f"https://twitter.com/{username}") from e
            raise
