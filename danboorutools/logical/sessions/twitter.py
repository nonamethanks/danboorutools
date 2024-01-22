from __future__ import annotations

import json
import os
import time

import ring

from danboorutools import logger
from danboorutools.exceptions import DeadUrlError, NoCookiesForDomainError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, save_cookies_for


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
        attempts = 0
        while attempts < 5:
            follow_button = self.browser.find_elements("css selector", f"[aria-label='Following @{username}']")
            if follow_button and follow_button[0].text == "Following":
                logger.info("Subscribed successfully.")
                return
            attempts += 1
            time.sleep(1)
        raise NotImplementedError(follow_button.text, username)

    @ring.lru()
    def browser_login(self) -> None:
        try:
            self.browser.load_cookies("twitter")
            self.browser.get("https://twitter.com/home")
            elements = self.browser.find_elements("css selector", ".public-DraftEditorPlaceholder-inner")
        except NoCookiesForDomainError:
            self._do_login()
        else:
            if not elements:
                self._do_login()

    def _do_login(self) -> None:
        logger.info("Logging in to twitter...")
        self.browser.delete_all_cookies()
        self.browser.get("https://twitter.com/login")

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

        self.browser.get("https://twitter.com/home")
        self.browser.find_element("css selector", ".public-DraftEditorPlaceholder-inner")

        save_cookies_for("twitter", self.browser.get_cookies())
        logger.trace("Successfully logged in in to twitter.")

    def user_data(self, user_name: str | None = None, user_id: int | None = None) -> TwitterUserData:
        csrf_token = os.environ["TWITTER_CSRF"]
        auth_token = os.environ["TWITTER_AUTH"]

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
            "cookie": f"lang=en; auth_token={auth_token}; ct0={csrf_token}; ",
            "x-csrf-token": csrf_token,
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

        response = self.get(
            graphql_url,
            params=params,
            headers=headers,
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


class TwitterUserData(BaseModel):
    id: int
    name: str
    screen_name: str
    entities: dict[str, dict[str, list[dict]]] | None

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
