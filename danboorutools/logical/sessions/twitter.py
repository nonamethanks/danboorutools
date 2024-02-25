from __future__ import annotations

import json
import os
import time
from datetime import datetime

import ring
from pydantic import field_validator

from danboorutools import logger
from danboorutools.exceptions import DeadUrlError, NoCookiesForDomainError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, save_cookies_for
from danboorutools.util.time import datetime_from_string


def _twitter_login_through_form(self: Session) -> None:
    logger.info("Logging in to twitter...")

    username_field = self.browser.find_element("css selector", "[autocomplete='username']")
    username_field.send_keys(os.environ["TWITTER_EMAIL"])
    self.browser.find_element("css selector", ":has([autocomplete='username']) + div[role='button']").click()

    time.sleep(1)

    if self.browser.find_elements_by_text("There was unusual login activity", full_match=False):
        username_input = self.browser.find_elements_by_text("Phone or username")[0]\
            .find_element("xpath", "../../..").find_element("css selector", "input")
        username_input.send_keys(os.environ["TWITTER_USERNAME"])
        self.browser.find_elements_by_text("Next")[0].click()
        time.sleep(1)

    password_field = self.browser.find_element("css selector", "[autocomplete='current-password'][name='password']")
    password_field.send_keys(os.environ["TWITTER_PASSWORD"])
    self.browser.find_elements_by_text("Log in")[0].click()

    time.sleep(1)

    if self.browser.find_elements_by_text("Confirmation code"):
        raise NotImplementedError("Twitter is asking for confirmation email.")


class TwitterSession(Session):
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"  # noqa: S105

    def subscribe(self, username: str) -> None:
        self.browser_login()
        self.browser.get(f"https://twitter.com/{username}")

        if self.browser.find_elements("css selector", f"[aria-label='Following @{username}']"):
            logger.info("Already subscribed.")
            return

        follow_button = self.browser.find_element("css selector", f"[aria-label='Follow @{username}']")
        follow_button.click()

        if self.browser.find_elements_by_text("Your account is suspended", full_match=False):
            raise NotImplementedError("Twitter account is suspended.")
        attempts = 0
        while attempts < 5:
            following_button = self.browser.find_elements("css selector", f"[aria-label='Following @{username}']")
            if following_button and following_button[0].text == "Following":
                logger.info("Subscribed successfully.")
                return
            attempts += 1
            time.sleep(1)

        raise NotImplementedError(follow_button.text, username)

    @ring.lru()
    def browser_login(self) -> None:
        try:
            self.browser.load_cookies("twitter")
        except NoCookiesForDomainError:
            pass
        else:
            self.browser.get("https://twitter.com/home")
            elements = self.browser.find_elements("css selector", ".public-DraftEditorPlaceholder-inner")
            if elements:
                return

        self.browser.delete_all_cookies()
        self.browser.get("https://twitter.com/login")
        self._do_login()
        self.browser.get("https://twitter.com/home")
        self.browser.find_element("css selector", ".public-DraftEditorPlaceholder-inner")
        save_cookies_for("twitter", self.browser.get_cookies())
        logger.trace("Successfully logged in in to twitter.")

    _do_login = _twitter_login_through_form

    @property
    def _twitter_headers(self) -> dict[str, str]:
        csrf_token = os.environ["TWITTER_CSRF"]
        auth_token = os.environ["TWITTER_AUTH"]

        return {
            "authorization": f"Bearer {self.BEARER_TOKEN}",
            "cookie": f"lang=en; auth_token={auth_token}; ct0={csrf_token}; ",
            "x-csrf-token": csrf_token,
        }

    def user_data(self, user_name: str | None = None, user_id: int | None = None) -> TwitterUserData:
        if user_name:
            endpoint = "G3KGOASz96M-Qu0nwmGXNg/UserByScreenName"
            variables = f'{{"screen_name":"{user_name}","withSafetyModeUserFields":true}}'
        elif user_id:
            endpoint = "QdS5LJDl99iL_KUzckdfNQ/UserByRestId"
            variables = f'{{"userId":"{user_id}","withSafetyModeUserFields":true}}'
        else:
            raise ValueError

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
        }

        graphql_url = f"https://twitter.com/i/api/graphql/{endpoint}"

        response = self.get(
            graphql_url,
            params=params,
            headers=self._twitter_headers.copy(),
        )
        data = response.json()

        if not data:
            raise DeadUrlError(response=response)

        if "user" in data:
            user_data = data["user"]
        elif "data" in data:
            try:
                user_data = data["data"]["user"]
            except KeyError as e:
                if data["data"] == {}:
                    raise DeadUrlError(response) from e
                else:
                    raise
        else:
            raise NotImplementedError(data)

        if not user_data:
            raise DeadUrlError(response=response)

        try:
            old_user_data = user_data["result"]["legacy"]
        except KeyError as e:
            if user_data["result"]["message"] == "User is suspended":
                raise DeadUrlError(response=response) from e
            raise

        return TwitterUserData(**old_user_data | {"id": user_data["result"]["rest_id"]})

    def get_feed(self, cursor: str | None = None) -> TwitterPageOfMediaResults:
        variables = {
            "count": 40,
            "includePromotedContent": False,
            "latestControlAvailable": True,
            "requestContext": "ptr",
        }

        features = {
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_media_download_video_enabled": False,
            "responsive_web_enhance_cards_enabled": False,
        }

        if cursor:
            variables["cursor"] = cursor

        params = {
            "variables": json.dumps(variables, separators=(",", ":")),
            "features": json.dumps(features, separators=(",", ":")),
        }

        response = self.get(
            "https://twitter.com/i/api/graphql/J1AQiEIiEDyF-1zgyrXHCA/HomeLatestTimeline",
            params=params,
            headers=self._twitter_headers,
        )

        instructions = response.json()["data"]["home"]["home_timeline_urt"]["instructions"]
        return self.__parse_timeline_instructions(instructions)

    def get_user_media(self, user_id: int, cursor: str | None = None) -> TwitterPageOfMediaResults:
        features = {
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": False,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_media_download_video_enabled": False,
            "responsive_web_enhance_cards_enabled": False,
        }

        variables = {
            "userId": user_id,
            "count": 20,
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
            "withV2Timeline": True,
        }

        if cursor:
            variables["cursor"] = cursor

        params = {
            "variables": json.dumps(variables, separators=(",", ":")),
            "features": json.dumps(features, separators=(",", ":")),
        }

        response = self.get(
            "https://twitter.com/i/api/graphql/cEjpJXA15Ok78yO4TUQPeQ/UserMedia",
            params=params,
            headers=self._twitter_headers,
        )
        timeline_instructions: list[dict] = response.json()["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
        collected_instructions = []
        for instr in timeline_instructions:
            if instr.get("content"):
                content = instr.get("content") | {"type": instr["entryType"]}
            elif instr.get("type") in ["TimelineClearCache", "TimelineTerminateTimeline"]:
                continue
            elif instr.get("type") in ["TimelineAddEntries", "TimelineAddToModule"]:
                content = instr
            else:
                raise NotImplementedError(instr)

            collected_instructions.append(content)

        return self.__parse_timeline_instructions(collected_instructions)

    def __parse_timeline_instructions(self, timeline_instructions: list[dict]) -> TwitterPageOfMediaResults:
        entries = []
        next_cursor: str | None = None

        for instruction in timeline_instructions:
            if instruction["type"] in ["TimelineClearCache", "TimelineTerminateTimeline"]:
                continue
            if instruction["type"] == "TimelineAddEntries":
                for sub_instruction in instruction["entries"]:
                    if sub_instruction["content"]["entryType"] == "TimelineTimelineCursor":
                        if sub_instruction["content"]["cursorType"] == "Top":
                            continue
                        elif sub_instruction["content"]["cursorType"] == "Bottom":
                            next_cursor = sub_instruction["content"]["value"]
                        else:
                            raise NotImplementedError(sub_instruction)
                    elif sub_instruction["content"]["entryType"] == "TimelineTimelineModule":
                        entries += [
                            entry["item"]["itemContent"] | {"__original_data": entry}
                            for entry in sub_instruction["content"]["items"]
                        ]
                    elif sub_instruction["content"]["entryType"] == "TimelineTimelineItem":
                        entries.append(sub_instruction["content"]["itemContent"] | {"__original_data": sub_instruction})  # feed
                    else:
                        raise NotImplementedError(sub_instruction)
                continue
            elif instruction["type"] == "TimelineAddToModule":
                entries += [
                    entry["item"]["itemContent"] | {"__original_data": entry}
                    for entry in instruction["moduleItems"]
                ]
                continue
            raise NotImplementedError(instruction)

        tweets = []
        for entry in entries:
            if entry["itemType"] == "TimelineTweet":
                if entry.get("promotedMetadata"):
                    continue

                if not entry["tweet_results"]:
                    continue  # why the fuck would this be empty?

                try:
                    tweet_result = entry["tweet_results"]["result"]
                except KeyError as e:
                    raise NotImplementedError(entry) from e

                if "tweet" in tweet_result:
                    tweet_result = tweet_result["tweet"]
                legacy_data = tweet_result["legacy"]
                tweets.append(TwitterTimelineTweetData(**legacy_data))
            elif entry["itemType"] in ["TimelineMessagePrompt", "TimelineUser"]:
                continue  # fuck off with these ads
            else:
                raise NotImplementedError(entry)

        if not entries:
            next_cursor = None
        return TwitterPageOfMediaResults(next_cursor=next_cursor, tweets=tweets)


class TwitterPageOfMediaResults(BaseModel):
    next_cursor: str | None
    tweets: list[TwitterTimelineTweetData]


class TwitterTimelineTweetData(BaseModel):
    id_str: int

    favorite_count: int
    created_at: datetime
    entities: dict

    retweeted_status_result: dict | None = None  # whether something's a retweet

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_created_at(cls, value: str) -> datetime:
        return datetime_from_string(value)

    @property
    def assets(self) -> list[str]:
        if "media" not in self.entities:
            return []

        extracted = []
        for entity in self.entities["media"]:
            if entity["type"] == "photo":
                extracted.append(entity["media_url_https"])
            elif entity["type"] == "video":
                variants = entity["video_info"]["variants"]
                biggest_url = max(variants, key=lambda x: x.get("bitrate", 0))["url"]
                extracted.append(biggest_url)
            elif entity["type"] == "animated_gif":
                variants = entity["video_info"]["variants"]
                biggest_url = max(variants, key=lambda x: x.get("bitrate", 0))["url"]
                extracted.append(biggest_url)
            else:
                raise NotImplementedError(entity)

        return extracted


class TwitterUserData(BaseModel):
    id: int
    name: str
    screen_name: str
    entities: dict[str, dict[str, list[dict]]] | None

    profile_image_url_https: str
    profile_banner_url: str | None = None

    @property
    def related_urls(self) -> list[Url]:
        related: list[Url] = []

        assert self.entities  # so far i only found this == None if from tweet data
        urls = self.entities.get("url", {}).get("urls", [])
        description_urls = self.entities.get("description", {}).get("urls", [])
        for field in urls + description_urls:  # need to be careful here for bullshit links
            # though usually if they link other people they'll do an @, which doesn't end up appearing in the entities
            if not (url_string := field["expanded_url"]).endswith("..."):
                related += [Url.parse(url_string)]

        return related
