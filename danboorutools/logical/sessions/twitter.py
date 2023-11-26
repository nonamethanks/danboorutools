from __future__ import annotations

import json
import os

from danboorutools.exceptions import DeadUrlError

# from datetime import datetime
# from typing import TYPE_CHECKING
# from pydantic import field_validator
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel

# from danboorutools.util.time import datetime_from_string

# if TYPE_CHECKING:
#    from danboorutools.logical.urls.twitter import TwitterAssetUrl

# SUSPENSION_MSG = "@{screen_name}'s account is temporarily unavailable because it violates the Twitter Media Policy. Learn more."


class TwitterSession(Session):
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"  # noqa: S105
    CSRF_TOKEN = os.environ["TWITTER_CSRF"]
    AUTH_TOKEN = os.environ["TWITTER_AUTH"]

    def user_data(self, user_name: str | None = None, user_id: int | None = None) -> TwitterUserData:
        if user_name:
            endpoint = "G3KGOASz96M-Qu0nwmGXNg/UserByScreenName"
            variables = f'{{"screen_name":"{user_name}","withSafetyModeUserFields":true}}'
        elif user_id:
            endpoint = "QdS5LJDl99iL_KUzckdfNQ/UserByRestId"
            variables = f'{{"userId":"{user_id}","withSafetyModeUserFields":true}}'
        else:
            raise ValueError

        headers = {
            "authorization": f"Bearer {self.BEARER_TOKEN}",
            "cookie": f"lang=en; auth_token={self.AUTH_TOKEN}; ct0={self.CSRF_TOKEN}; ",
            "x-csrf-token": self.CSRF_TOKEN,
        }

        features = {
            "hidden_profile_likes_enabled": True,
            "hidden_profile_subscriptions_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "subscriptions_verification_info_is_identity_verified_enabled": True,
            "subscriptions_verification_info_verified_since_enabled": True,
            "highlights_tweets_tab_ui_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
        }

        params = {
            "variables": variables,
            "features": json.dumps(features, separators=(",", ":")),
            "fieldToggles": '{"withAuxiliaryUserLabels":false}',
        }

        graphql_url = f"https://twitter.com/i/api/graphql/{endpoint}"

        data = self.get_json(
            graphql_url,
            params=params,
            headers=headers,
        )["data"]

        if not data:
            raise DeadUrlError(original_url=graphql_url, status_code=200)

        try:
            if not (user_data := data["user"]):
                raise DeadUrlError(original_url=graphql_url, status_code=200)
        except KeyError:
            # motherfucking cunt
            print(data)  # noqa: T201
            raise

        try:
            old_user_data = user_data["result"]["legacy"]
        except KeyError as e:
            if user_data["result"]["message"] == "User is suspended":
                raise DeadUrlError(original_url=graphql_url, status_code=200) from e
            raise

        return TwitterUserData(**old_user_data | {"id": user_data["result"]["rest_id"]})


class TwitterUserData(BaseModel):
    id: int
    name: str
    screen_name: str
    entities: dict[str, dict[str, list[dict]]] | None

    @property
    def related_urls(self) -> list[Url]:
        related: list[Url] = []
        from danboorutools.logical.urls.twitter import TwitterIntentUrl

        related += [TwitterIntentUrl.build(intent_id=self.id)]

        assert self.entities  # so far i only found this == None if from tweet data
        urls = self.entities.get("url", {}).get("urls", [])
        description_urls = self.entities.get("description", {}).get("urls", [])
        for field in urls + description_urls:  # need to be careful here for bullshit links
            # though usually if they link other people they'll do an @, which doesn't end up appearing in the entities
            if not (url_string := field["expanded_url"]).endswith("..."):
                related += [Url.parse(url_string)]

        return related


# class TwitterTweetData(BaseModel):
#     id: int
#     created_at: datetime
#     favorite_count: int
#     extended_entities: dict[str, list[dict]] | None

#     user: TwitterUserData

#     @field_validator("created_at", mode="before")
#     @classmethod
#     def parse_created_at(cls, value: str) -> datetime:
#         return datetime_from_string(value)

#     @property
#     def asset_urls(self) -> list[TwitterAssetUrl]:
#         from danboorutools.logical.urls.twitter import TwitterAssetUrl

#         if not self.extended_entities:
#             return []

#         assets = []
#         for item in self.extended_entities["media"]:
#             if item["type"] == "photo":
#                 asset_str = item["media_url"] + ":orig"
#             elif item["type"] == "animated_gif":
#                 variants = item["video_info"]["variants"]
#                 if len(variants) == 1:
#                     asset_str = variants[0]["url"]
#                 else:
#                     raise NotImplementedError(variants)
#             elif item["type"] == "video":
#                 variants = item["video_info"]["variants"]
#                 sorted_variants = sorted(variants, key=lambda k: k.get("bitrate", 0))
#                 asset_str = sorted_variants[-1]["url"]
#             else:
#                 raise NotImplementedError(item)

#             parsed = Url.parse(asset_str)
#             assert isinstance(parsed, TwitterAssetUrl)
#             assets.append(parsed)

#         return assets
