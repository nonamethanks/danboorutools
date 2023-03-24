from __future__ import annotations

import os
from functools import cached_property

import twitter

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, memoize


class TwitterSession(Session):

    @cached_property
    def api(self) -> twitter.Api:
        consumer_key = os.environ["TWITTER_CONSUMER_KEY"]
        consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]
        access_token = os.environ["TWITTER_ACCESS_TOKEN"]
        access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

        return twitter.Api(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            sleep_on_rate_limit=True,
            tweet_mode="extended",
        )

    @memoize
    def user_data(self, username: str | None = None, user_id: int | None = None) -> TwitterUserData:
        assert username or user_id
        try:
            return TwitterUserData(**self.api.GetUser(screen_name=username, user_id=user_id, return_json=True, include_entities=True))
        except twitter.error.TwitterError as e:
            if "User not found." in str(e) or "User has been suspended." in str(e):
                original_url = f"https://twitter.com/{username}" if username else f"https://twitter.com/intent/user?user_id={user_id}"
                raise DeadUrlError(status_code=404, original_url=original_url) from e
            raise


class TwitterUserData(BaseModel):
    id: int
    name: str
    screen_name: str
    entities: dict[str, dict[str, list[dict]]]

    @property
    def related_urls(self) -> list[Url]:
        related: list[Url] = []
        from danboorutools.logical.urls.twitter import TwitterIntentUrl

        related += [Url.build(TwitterIntentUrl, intent_id=self.id)]

        urls = self.entities.get("url", {}).get("urls", [])
        description_urls = self.entities.get("description", {}).get("urls", [])
        for field in urls + description_urls:  # need to be careful here for bullshit links
            # though usually if they link other people they'll do an @, which doesn't end up appearing in the entities
            if not (url_string := field["expanded_url"]).endswith("..."):
                related += [Url.parse(url_string)]

        return related
