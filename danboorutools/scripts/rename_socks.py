import os

from danboorutools import logger
from danboorutools.logical.sessions.danbooru import danbooru_api

logger.log_to_file()

sock_message = os.environ["DANBOORUTOOLS_SOCKPUPPET_AUTORENAME_MESSAGE"].strip()
if not sock_message:
    raise NotImplementedError("No sock message selected.")

if "sockpuppet of user #" not in sock_message.lower():
    raise NotImplementedError("Message must be like 'Sockpuppet of user #'")


def main() -> None:
    logger.info(f"Searching for ban messages containing '{sock_message}'...")
    bans = danbooru_api.bans(reason_matches=sock_message)
    for ban in bans:
        banned_user = ban.user
        old_name = banned_user.name
        new_name = banned_user.id

        if not old_name.startswith(str(new_name)):
            logger.info(f"Renaming {banned_user.url} {old_name} -> {new_name}")
            assert banned_user.is_banned  # you never know man
            danbooru_api.rename_user(user_id=banned_user.id, new_name=new_name)
            logger.info(f"User {banned_user.url} {old_name} renamed to {new_name}")
