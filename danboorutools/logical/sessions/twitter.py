from __future__ import annotations

import os
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING

import ring
import twitter
from pydantic import validator

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from danboorutools.logical.urls.twitter import TwitterAssetUrl

SUSPENSION_MSG = "@{screen_name}'s account is temporarily unavailable because it violates the Twitter Media Policy. Learn more."


class TwitterSession(Session):

    @cached_property
    def api(self) -> twitter.Api:
        consumer_key = os.environ["TWITTER_CONSUMER_KEY"]
        consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]
        access_token = os.environ["TWITTER_ACCESS_TOKEN"]
        access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

        api = twitter.Api(
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            sleep_on_rate_limit=True,
            tweet_mode="extended",
        )
        api._session = self
        return api

    @ring.lru()
    def user_data(self, username: str | None = None, user_id: int | None = None) -> TwitterUserData:
        assert username or user_id
        try:
            return TwitterUserData(**self.api.GetUser(screen_name=username, user_id=user_id, return_json=True, include_entities=True))
        except twitter.error.TwitterError as e:
            if "User not found." in str(e) or "User has been suspended." in str(e):
                original_url = f"https://twitter.com/{username}" if username else f"https://twitter.com/intent/user?user_id={user_id}"
                raise DeadUrlError(status_code=404, original_url=original_url) from e
            raise

    @ring.lru()
    def get_user_tweets(self, user_id: int, max_id: int, since_id: int) -> list[TwitterTweetData]:
        url = f"{self.api.base_url}/statuses/user_timeline.json"

        parameters = {
            "user_id": user_id,
            "since_id": since_id or None,
            "max_id": max_id or None,
            "count": 200,
            "include_rts": False,
            "trim_user": False,
            "exclude_replies": False,
        }

        resp = self.api._RequestUrl(url, "GET", data=parameters)
        data = self.api._ParseAndCheckTwitter(resp.content.decode("utf-8"))
        return [TwitterTweetData(**tweet) for tweet in data]


class TwitterUserData(BaseModel):
    id: int
    name: str
    screen_name: str
    entities: dict[str, dict[str, list[dict]]] | None

    @property
    def related_urls(self) -> list[Url]:
        related: list[Url] = []
        from danboorutools.logical.urls.twitter import TwitterIntentUrl

        related += [Url.build(TwitterIntentUrl, intent_id=self.id)]

        assert self.entities  # so far i only found this == None if from tweet data
        urls = self.entities.get("url", {}).get("urls", [])
        description_urls = self.entities.get("description", {}).get("urls", [])
        for field in urls + description_urls:  # need to be careful here for bullshit links
            # though usually if they link other people they'll do an @, which doesn't end up appearing in the entities
            if not (url_string := field["expanded_url"]).endswith("..."):
                related += [Url.parse(url_string)]

        return related


class TwitterTweetData(BaseModel):
    id: int
    created_at: datetime
    favorite_count: int
    extended_entities: dict[str, list[dict]] | None

    user: TwitterUserData

    @validator("created_at", pre=True)
    def parse_created_at(cls, value: str) -> datetime:  # pylint: disable=no-self-argument # noqa: N805 # pydantic is retarded
        return datetime_from_string(value)

    @property
    def asset_urls(self) -> list[TwitterAssetUrl]:
        from danboorutools.logical.urls.twitter import TwitterAssetUrl
        if not self.extended_entities:
            return []

        assets = []
        for item in self.extended_entities["media"]:
            if item["type"] == "photo":
                asset_str = item["media_url"] + ":orig"
            elif item["type"] == "animated_gif":
                variants = item["video_info"]["variants"]
                if len(variants) == 1:
                    asset_str = variants[0]["url"]
                else:
                    raise NotImplementedError(variants)
            elif item["type"] == "video":
                variants = item["video_info"]["variants"]
                sorted_variants = sorted(variants, key=lambda k: k.get("bitrate", 0))
                asset_str = sorted_variants[-1]["url"]
            else:
                raise NotImplementedError(item)

            parsed = Url.parse(asset_str)
            assert isinstance(parsed, TwitterAssetUrl)
            assets.append(parsed)

        return assets
