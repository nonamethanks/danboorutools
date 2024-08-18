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

from danboorutools import logger, settings
from danboorutools.logical.progress_tracker import ProgressTracker
from danboorutools.logical.sessions.danbooru import DanbooruApi, danbooru_api
from danboorutools.models.danbooru import DanbooruUser, DanbooruUserEvent
from danboorutools.util.misc import BaseModel

SOCK_AUTOBAN_MESSAGE = os.environ["DANBOORUTOOLS_SOCKPUPPET_AUTORENAME_MESSAGE"].strip()
if SOCK_AUTOBAN_MESSAGE and "sockpuppet of user #" not in SOCK_AUTOBAN_MESSAGE.lower():
    raise NotImplementedError("Message must be like 'Sockpuppet of user #'")
SOCK_AUTOBAN_CARRIER = os.environ["DANBOORUTOOLS_SOCKPUPPET_AUTOBAN_CARRIER"].strip()
SOCK_AUTOBAN_IP_PREFIXES = os.environ["DANBOORUTOOLS_SOCKPUPPET_AUTOBAN_IP_PREFIX"].strip().split(",")

sock_config = yaml.safe_load(Path(settings.BASE_FOLDER / "sock_config.yaml").read_text(encoding="utf-8"))
SOCK_PATTERNS = [re.compile(p, re.I) for p in sock_config["patterns"]]


class SockpuppetDetector:
    def __init__(self, mode: Literal["test", "production"] = "test"):
        self.mode = mode
        if self.mode == "production":
            self.webhook_url = os.environ["DISCORD_SOCKPUPPET_CHANNEL_WEBHOOK"]
            self.dapi = danbooru_api
        elif self.mode == "test":
            self.webhook_url = os.environ["DISCORD_SOCKPUPPET_CHANNEL_WEBHOOK_TEST"]
            self.dapi = DanbooruApi(domain="testbooru")
        else:
            raise ValueError(self.mode)

        self.last_checked_session = ProgressTracker("SOCKPUPPET_DETECTOR_LAST_CHECKED_SESSION", 0)
        self.old_hooks = ProgressTracker[list[dict]]("SOCKPUPPET_DETECTOR_POSTED_HOOKS", [])

        self.max_webhook_backchecking = 20

        if SOCK_AUTOBAN_MESSAGE:
            logger.info(f"<r>Will autoban any user whose previous ban reason started with '{SOCK_AUTOBAN_MESSAGE}'</r>")
        if SOCK_AUTOBAN_CARRIER and SOCK_AUTOBAN_IP_PREFIXES:
            logger.info(f"<r>Will autoban any user with certain names and carrier == '{SOCK_AUTOBAN_CARRIER}' "
                        f"and IP starting with {SOCK_AUTOBAN_IP_PREFIXES}</r>")

            logger.info("<r>Configured autoban patterns:</r>")
            for pattern in SOCK_PATTERNS:
                logger.info(f">  <r>{pattern}</r>")

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
                if SOCK_AUTOBAN_CARRIER and SOCK_AUTOBAN_IP_PREFIXES:
                    self._check_for_sock(signup, [])
                continue

            other_users_map = {event.user.id: event.user for event in other_events}
            other_users = [name for _id, name in sorted(other_users_map.items(), key=lambda x: x[0])]

            if SOCK_AUTOBAN_CARRIER and SOCK_AUTOBAN_IP_PREFIXES and self._check_for_sock(signup, other_users):
                for signup in signups:  # noqa: PLW2901 # be silent machine, I know what I'm doing
                    if signup.user.id in [user.id for user in other_users]:
                        signup.user.is_banned = True
                continue

            previous_ban_reasons: list[str] = [ban["reason"] for user in other_users for ban in user._raw_data["bans"]]
            if previous_ban_reasons:
                shared_account_reasons = ["shared account", "publicly shared account"]
                if all(r.lower().strip().strip(".") in shared_account_reasons for r in previous_ban_reasons):
                    continue

                if SOCK_AUTOBAN_MESSAGE and any(ban_r.lower().startswith(SOCK_AUTOBAN_MESSAGE.lower()) for ban_r in previous_ban_reasons):
                    user_to_ban = signup.user
                    if not user_to_ban.is_banned:
                        self.ban_user(user_to_ban, validate=True)

                    if user_to_ban.name != str(user_to_ban.id):
                        logger.info(f"<r>RENAMING USER {user_to_ban} {user_to_ban.name} -> '{user_to_ban.id}' </r>")
                        danbooru_api.rename_user(user_to_ban.id, new_name=user_to_ban.id)

            found.append({
                "sock": signup.user,
                "session_id": signup.user_session.session_id,
                "other_users": other_users,
            })

        return found

    def ban_user(self, user_to_ban: DanbooruUser, validate: bool = True) -> None:
        if validate:
            assert user_to_ban.level <= 20
            assert user_to_ban.created_at
            assert user_to_ban.created_at > (datetime.datetime.now(tz=UTC) - datetime.timedelta(hours=1))

        logger.info(f"<r>BANNING USER {user_to_ban}</r>")
        danbooru_api.ban_user(user_to_ban.id, reason=SOCK_AUTOBAN_MESSAGE)

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

    def _check_for_sock(self, signup: DanbooruUserEvent, other_users: list[DanbooruUser]) -> bool:
        if not any(pattern.search(signup.user.name) for pattern in SOCK_PATTERNS):
            return False

        logger.info(f"User {signup.user} matches name regex")

        last_ip_addr: str = signup.user._raw_data["last_ip_addr"]
        if not last_ip_addr.startswith(tuple(SOCK_AUTOBAN_IP_PREFIXES)):
            return False

        logger.info(f"User {signup.user} matches ip prefix {SOCK_AUTOBAN_IP_PREFIXES}.")

        ip_addr_data = danbooru_api.danbooru_request("GET", f"ip_addresses/{last_ip_addr}.json")
        if ip_addr_data["carrier"].lower() != SOCK_AUTOBAN_CARRIER.lower():
            return False

        logger.info(f"User {signup.user} matches carrier {SOCK_AUTOBAN_CARRIER}")

        user_to_ban = signup.user
        if len([u for u in other_users if not u.is_banned]) > 20:
            raise NotImplementedError("Something's wrong, too many unbanned users.")

        self.ban_user(user_to_ban)
        if user_to_ban.name != str(user_to_ban.id):
            logger.info(f"<r>RENAMING USER {user_to_ban} {user_to_ban.name} -> '{user_to_ban.id}' </r>")
            danbooru_api.rename_user(user_to_ban.id, new_name=user_to_ban.id)

        for other_user in other_users:
            assert other_user.level <= 20
            if not other_user.is_banned:
                self.ban_user(other_user, validate=False)
            if other_user.name != str(other_user.id):
                logger.info(f"<r>RENAMING USER {other_user} {other_user.name} -> '{other_user.id}' </r>")
                danbooru_api.rename_user(other_user.id, new_name=other_user.id)

        return True


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
    id: int  # noqa: A003
    username: str

    embeds: list[HookEmbed]


@click.command()
@click.argument("mode", type=click.Choice(["test", "production"]))
def main(mode: Literal["test", "production"]) -> None:
    SockpuppetDetector(mode=mode).detect_and_post()
