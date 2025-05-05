from __future__ import annotations

import datetime
import os
import re
import time
from datetime import UTC
from pathlib import Path
from typing import Literal

import click
import yaml
from discord_webhook import DiscordEmbed, DiscordWebhook
from pydantic import Field

from danboorutools import logger, settings
from danboorutools.logical.progress_tracker import ProgressTracker
from danboorutools.logical.sessions.danbooru import danbooru_api, testbooru_api
from danboorutools.models.danbooru import DanbooruUser, DanbooruUserEvent
from danboorutools.util.misc import BaseModel


class BanEvader(BaseModel):
    name: str
    ban_message: str = Field(min_length=3)
    carrier: str | None = None
    carrier_organization: str | None = None
    country: str | None = None
    ip_prefixes: list[str] | None = None
    name_patterns: list[str]
    rename_socks: bool = False
    ban_proxies: bool = False

    def log_intro(self) -> None:
        logger.info(f"  <r>{self.name} ({self.ban_message})</r>")
        logger.info(f"    <r>Carrier: {self.carrier}</r>")
        logger.info(f"    <r>Carrier org: {self.carrier_organization}</r>")
        logger.info(f"    <r>Country: {self.carrier_organization}</r>")
        logger.info(f"    <r>IP prefixes: {', '.join(self.ip_prefixes) if self.ip_prefixes else None}</r>")
        logger.info(f"    <r>Autoban proxies: {self.ban_proxies}</r>")
        logger.info(f"    <r>Rename socks: {self.rename_socks}</r>")
        logger.info( "    <r>Name patterns:</r>")
        for pattern in self.name_patterns:
            logger.info(f"        <r>{pattern}</r>")

    @property
    def compiled_name_patterns(self) -> list[re.Pattern]:
        return [re.compile(p, re.IGNORECASE) for p in self.name_patterns]


    def signup_is_sock(self, signup: DanbooruUserEvent) -> bool:  # noqa: PLR0911
        logger.info(f"Checking user {signup.user} against pattern for ban evader {self.name}...")

        if not any(pattern.search(signup.user.name) for pattern in self.compiled_name_patterns):
            logger.info(f"User {signup.user} does not match name regex. Aborting.")
            return False
        logger.info(f"User {signup.user} matches name regex")

        if not self.ip_prefixes and not self.carrier and not self.carrier_organization and not self.ban_proxies and not self.country:
            raise ValueError("No IP prefixes, carrier, carrier organization, country or proxy ban configured. "
                             "Please check your sock_config.yaml file.")

        if self.ip_prefixes and not self.check_ip_prefixes(signup):
            return False

        if self.carrier and not self.check_ip_data(signup, "carrier", self.carrier):
            return False

        if self.carrier_organization and not self.check_ip_data(signup, "organization", self.carrier_organization):
            return False

        if self.country and not self.check_ip_data(signup, "country", self.country):
            return False

        if self.ban_proxies and not self.check_ip_data(signup, "is_proxy", True):  # noqa: SIM103
            return False

        return True

    def check_ip_prefixes(self, signup: DanbooruUserEvent) -> bool:
        last_ip_addr: str = signup.user._raw_data["last_ip_addr"]
        if self.ip_prefixes:
            if not last_ip_addr.startswith(self.ip_prefixes):
                logger.info(f"User {signup.user} does not match IP prefixes. Aborting.")
                return False
            logger.info(f"User {signup.user} matches IP prefixes {self.ip_prefixes}")

        return True

    @staticmethod
    def check_ip_data(signup: DanbooruUserEvent, key: str, expected: str | bool) -> bool:
        last_ip_addr: str = signup.user._raw_data["last_ip_addr"]
        ip_addr_data = danbooru_api.danbooru_request("GET", f"ip_addresses/{last_ip_addr}.json")
        if (found := ip_addr_data[key]) is None:
            return False
        if isinstance(expected, str):
            check = found.lower() == expected.lower()
        elif isinstance(expected, bool):
            check = found is expected
        else:
            raise TypeError(f"Expected value {expected} of type {type(expected)} is not a string or boolean.")

        if check:
            logger.info(f"User {signup.user} '{signup.user.name}': Value for '{key}' '{found}' (type {type(found)}) "
                        f"does not match expected value '{expected}' (type {type(expected)}).")
            return False
        else:
            logger.info(f"User {signup.user} '{signup.user.name}': Value for '{key}' '{found}' matches expected value '{expected}'.")
            return True




sock_config = yaml.safe_load(Path(settings.BASE_FOLDER / "sock_config.yaml").read_text(encoding="utf-8"))
ban_evaders = [BanEvader(**evader) for evader in sock_config["socks"]]


class SockpuppetDetector:
    def __init__(self, mode: Literal["test", "production"] = "test"):
        self.mode = mode
        if self.mode == "production":
            self.webhook_url = os.environ["DISCORD_SOCKPUPPET_CHANNEL_WEBHOOK"]
            self.dapi = danbooru_api
        elif self.mode == "test":
            self.webhook_url = os.environ["DISCORD_SOCKPUPPET_CHANNEL_WEBHOOK_TEST"]
            self.dapi = testbooru_api
        else:
            raise ValueError(self.mode)

        self.enable_autobans = os.environ.get("SOCKPUPPET_CHECK_ENABLE_AUTOBANS", "false").lower() in ["true", "1", "yes"]

        self.last_checked_session = ProgressTracker("SOCKPUPPET_DETECTOR_LAST_CHECKED_SESSION", 0)
        self.old_hooks = ProgressTracker[list[dict]]("SOCKPUPPET_DETECTOR_POSTED_HOOKS", [])

        self.max_webhook_backchecking = 20

        if ban_evaders:
            logger.info("<r>The following autobans are configured:</r>")
            for evader in ban_evaders:
                evader.log_intro()
                logger.info("")

    def detect_and_post(self) -> None:
        latest_signups = self.get_latest_signups()
        new_sockpuppets = self.detect_sockpuppets(*latest_signups)

        hooks = self.old_hooks.value
        for sock_data in new_sockpuppets:
            hooks += [self.send_to_discord(**sock_data)]

        self.update_posted_hooks(hooks)

        hooks_to_save = (hooks)[-self.max_webhook_backchecking:]

        self.old_hooks.value = hooks_to_save
        if not latest_signups:
            return
        self.last_checked_session.value = max(latest_signups, key=lambda x: x.id).id
        logger.info("Done.")

    def get_latest_signups(self) -> list[DanbooruUserEvent]:
        if self.last_checked_session.value:
            logger.info(f"Checking new account creations since ID {self.last_checked_session.value}...")
        else:
            logger.info("Checking new account creations...")

        id_query = f">{self.last_checked_session.value}" if self.last_checked_session.value else None
        latest_signups = self.dapi.user_events(category="user_creation", id=id_query)
        if not latest_signups:
            logger.info("No new account creations found.")
            return []

        logger.info(f"{len(latest_signups)} new account creations found. Checking...")
        if not self.last_checked_session.value:
            logger.info("Returning only the latest 20 results because it's the first scan.")
            return latest_signups[:20]
        return latest_signups

    def detect_sockpuppets(self, *signups: DanbooruUserEvent) -> list[dict]:
        found = []

        for index, signup in enumerate(signups):

            if (index+1) % 100 == 0:
                logger.info(f"Checking sockpuppets {index+1}/{len(signups)}")

            assert signup.user._raw_data["last_ip_addr"]  # for some reason it was returning empty
            if signup.user.is_banned:
                continue

            events = self.dapi.user_events(
                category_not="50,400,500,600",
                user_session={"session_id": signup.user_session.session_id},
            )

            if not (other_events := [e for e in events if e.user.name != signup.user.name]):
                for ban_evader in ban_evaders:
                    self._check_for_sock(signup=signup, other_users=[], ban_evader=ban_evader)
                continue

            other_users_map = {event.user.id: event.user for event in other_events}
            other_users = [name for _id, name in sorted(other_users_map.items(), key=lambda x: x[0])]

            # have to do it all over again for signups from multiple accounts
            for ban_evader in ban_evaders:
                if self._check_for_sock(signup=signup, other_users=other_users, ban_evader=ban_evader):
                    for signup in signups:  # noqa: PLW2901 # be silent machine, I know what I'm doing
                        if signup.user.id in [user.id for user in other_users] and self.enable_autobans:
                            signup.user.is_banned = True
                    continue

            previous_ban_reasons: list[str] = [ban["reason"] for user in other_users for ban in user._raw_data["bans"]]
            if previous_ban_reasons:
                shared_account_reasons = ["shared account", "publicly shared account"]
                if all(r.lower().strip().strip(".") in shared_account_reasons for r in previous_ban_reasons):
                    continue

                for ban_evader in ban_evaders:
                    if any(ban_r.lower().startswith(ban_evader.ban_message.lower()) for ban_r in previous_ban_reasons):
                        user_to_ban = signup.user
                        if not user_to_ban.is_banned:
                            self.ban_user(user_to_ban, ban_evader=ban_evader, validate=True)

            found.append({
                "sock": signup.user,
                "session_id": signup.user_session.session_id,
                "other_users": other_users,
            })

        return found

    def ban_user(self, user_to_ban: DanbooruUser, ban_evader: BanEvader, validate: bool = True) -> None:
        if validate:
            assert user_to_ban.level <= 20
            assert user_to_ban.created_at
            assert user_to_ban.created_at > (datetime.datetime.now(tz=UTC) - datetime.timedelta(hours=1)), \
                f"Couldn't ban user {user_to_ban} '{user_to_ban.name}'"

        logger.info(f"<r>BANNING USER {user_to_ban} '{user_to_ban.name}' (sockpuppet of {ban_evader.name})</r>")
        if self.enable_autobans:
            danbooru_api.ban_user(user_to_ban.id, reason=ban_evader.ban_message)
        else:
            logger.info(f"Skipping autoban for {user_to_ban} '{user_to_ban.name}' because autobans are disabled.")
        if ban_evader.rename_socks and user_to_ban.name != str(user_to_ban.id):
            logger.info(f"<r>RENAMING USER {user_to_ban} '{user_to_ban.name}' -> '{user_to_ban.id}'</r>")
            if self.enable_autobans:
                danbooru_api.rename_user(user_to_ban.id, new_name=user_to_ban.id)
            else:
                logger.info(f"Skipping rename for {user_to_ban} '{user_to_ban.name}' because autobans are disabled.")

    def send_to_discord(self, sock: DanbooruUser, session_id: str,  other_users: list[DanbooruUser]) -> dict:
        webhook = DiscordWebhook(
            username="Sockpuppet Detection Bot",
            avatar_url="https://i.imgflip.com/3gnqzq.png",
            url=self.webhook_url,
        )

        embed = DiscordEmbed(title=sock.name, url=sock.url)

        first_sock, *other_socks = other_users
        embed.description = f"[Sock of {first_sock.name}"
        embed.description += f" and at least {len(other_socks)} other users" if other_socks else ""
        embed.description += f"]({self.dapi.base_url}/user_events?search[user_session][session_id]={session_id})"

        if any(banned_users := [user for user in other_users if user.is_banned]):
            embed.color = 15158332
            banned_ids = ",".join(str(user.id) for user in banned_users)
            ban_link = f"{self.dapi.base_url}/bans?search[user_id]={banned_ids}"
            str_count = "All" if len(banned_users) == len(other_users) else str(len(banned_users))
            embed.description += (
                f"\n:warning: {str_count} of these users [were already banned!]({ban_link}) :warning:")
        else:
            embed.color = 3447003
            embed.description += "\nNo previous ban detected."

        webhook.add_embed(embed)
        logger.info(f"Sending detected sockpuppet {sock.name} ({sock.url}) to channel.")

        response = webhook.execute()

        assert response.status_code in [200, 404], (response.status_code, response.content)

        time.sleep(2)
        return webhook.json

    def update_posted_hooks(self, hook_dicts: list[dict]) -> None:
        logger.info("Checking if old messages need update...")
        webhooks = [Hook(**h) for h in hook_dicts]
        ids_to_check = ",".join(str(embed.user_id) for webhook in webhooks for embed in webhook.embeds if not embed.deleted)
        user_map = {user.id: user for user in self.dapi.users(id=ids_to_check)}

        changed_count = 0
        for webhook in webhooks:
            changed = False
            webhook_to_send = DiscordWebhook(**webhook._raw_data, url=self.webhook_url)
            for old_embed, new_embed in zip(webhook.embeds, webhook_to_send.embeds, strict=True):
                if old_embed.deleted:
                    continue
                user = user_map[old_embed.user_id]
                if user.is_banned:
                    logger.info(f"Sending updated state for {user.name} ({user.url}) who got banned.")
                    new_embed["title"] = f"~~{old_embed.title}~~"
                    new_embed["description"] = f"~~{old_embed.description}~~"
                    new_embed["description"] += "\n\nThis user has been banned."
                    new_embed["color"] = 3066993
                    changed = True
                    changed_count += 1

            if changed:
                new_response = webhook_to_send.edit()
                assert new_response.status_code in [200, 404], new_response.json()
            if changed_count > 1:
                time.sleep(2)

        logger.info(f"Updated {changed_count} messages.")

    def _check_for_sock(self, signup: DanbooruUserEvent, other_users: list[DanbooruUser], ban_evader: BanEvader) -> bool:
        if not ban_evader.signup_is_sock(signup):
            return False

        user_to_ban = signup.user
        if len([u for u in other_users if not u.is_banned]) > 20:
            raise NotImplementedError("Something's wrong, too many unbanned users.")

        self.ban_user(user_to_ban, ban_evader=ban_evader)

        for other_user in other_users:
            assert other_user.level <= 20
            if not other_user.is_banned:
                self.ban_user(other_user, ban_evader=ban_evader, validate=False)

        return True


def rename_socks() -> None:
    for ban_evader in ban_evaders:
        if ban_evader.rename_socks:
            logger.info(f"Searching for ban messages containing '{ban_evader.ban_message}'...")
            bans = danbooru_api.bans(reason_matches=ban_evader.ban_message)
            for ban in bans:
                banned_user = ban.user
                old_name = banned_user.name
                new_name = banned_user.id

                if not old_name.startswith(str(new_name)):
                    logger.info(f"Renaming {banned_user.url} {old_name} -> {new_name}")
                    assert banned_user.is_banned  # you never know man
                    danbooru_api.rename_user(user_id=banned_user.id, new_name=new_name)
                    logger.info(f"User {banned_user.url} {old_name} renamed to {new_name}")


def delete_feedbacks() -> None:
    for evader in ban_evaders:
        if evader.rename_socks:
            logger.info(f"Searching for feedbacks to delete with message '{evader.ban_message}'...")
            feedbacks = danbooru_api.feedbacks(is_deleted=False, body_ilike=f"*{evader.ban_message}*")
            for feedback in feedbacks[:20]:
                if not feedback.user.is_banned:
                    continue
                printable_fb = feedback.body.replace("<", r"\<").replace(">", r"\>")
                logger.info(f"Deleting feedback '{printable_fb}' for user {feedback.user} because it matches the search.")
                danbooru_api.danbooru_request("PUT", f"{feedback.model_path}.json", json={"is_deleted": True})
            logger.info("Done.")




class HookEmbed(BaseModel):
    title: str
    description: str

    url: str

    @property
    def user_id(self) -> int:
        return DanbooruUser.id_from_url(self.url)

    @property
    def deleted(self) -> bool:
        return self.title.startswith("~~")


class Hook(BaseModel):
    id: int
    username: str

    embeds: list[HookEmbed]


@click.command()
@click.argument("mode", type=click.Choice(["test", "production"]))
def main(mode: Literal["test", "production"]) -> None:
    SockpuppetDetector(mode=mode).detect_and_post()
