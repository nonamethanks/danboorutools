import datetime
import os
import random
import sys

import redis
from billiard.einfo import ExceptionInfo
from celery.app.base import Celery
from celery.app.task import Task
from celery.schedules import crontab

from danboorutools import logger, settings
from danboorutools.exceptions import DanbooruHTTPError
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.scripts.create_artist_tags import add_artists_to_posts
from danboorutools.scripts.sockpuppet_discord_monitor import SockpuppetDetector, delete_feedbacks, rename_socks
from danboorutools.scripts.tag_paid_rewards_on_gelbooru import tag_paid_rewards_on_gelbooru
from danboorutools.util.mail import send_email

tasks = Celery("tasks", broker="redis://redis:6379/1", backend="redis://redis:6379/1")
DESTINATION_EMAIL = os.environ.get("EMAIL", None)
if DESTINATION_EMAIL:
    logger.info(f"Destination email for automatic errors: {DESTINATION_EMAIL} ")
else:
    logger.warning("No destination email set for automatic errors.")


class CeleryConfig:
    """Celery config options."""
    broker_connection_retry_on_startup = True
    worker_deduplicate_successful_tasks = True


tasks.config_from_object(CeleryConfig)


class CustomCeleryTask(Task):  # pylint: disable=abstract-method
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.redis_conn = redis.Redis(
            host="redis",
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
            socket_keepalive=False,
            health_check_interval=5,
            ssl_check_hostname=False,
        )

    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: ExceptionInfo) -> None:  # noqa: ARG002
        # https://gist.github.com/darklow/c70a8d1147f05be877c3
        # https://stackoverflow.com/a/45333231/1092940

        if not DESTINATION_EMAIL:
            return

        if isinstance(exc, DanbooruHTTPError) and "The database is unavailable. Try again later" in exc.error_message:
            return

        now = datetime.datetime.now(datetime.UTC).astimezone()
        pretty_name = self.name.replace("danboorutools.celery_tasks.", "")
        subject = f"Failure on task {pretty_name}, exc: {exc.__class__.__name__}"
        traceback: str = einfo.traceback
        message = f"The task {pretty_name} failed at {now} with the following exception:\n\n{traceback}"
        try:
            send_email(send_to=DESTINATION_EMAIL, message=message, subject=subject)
        except Exception as e:
            message = f"The task {pretty_name} failed at {now} but an email couldn't be delivered."
            logger.error(message)
            logger.exception(e)
            send_email(send_to=DESTINATION_EMAIL, message=message, subject=subject)

    def __call__(self, *args, **kwargs):
        self.setup_logger()

        lock_key = f"__celery_tasks_{self.name}__"

        if self.redis_conn.get(lock_key):
            logger.error(f"Another instance of the task {self.name} is running, skipping.")
            return None

        self.redis_conn.set(lock_key, "1", 60)
        result = super().__call__(*args, **kwargs)
        self.redis_conn.delete(lock_key)
        return result

    def setup_logger(self) -> None:
        loguru_colors = ["e", "c", "g", "m", "r"]
        loguru_colors += [f"l{c}" for c in loguru_colors]
        color = random.choice(loguru_colors)

        try:
            logger.remove()
        except FileNotFoundError:
            pass

        pretty_name = self.name.replace("danboorutools.celery_tasks.", "")

        logger_format = f"[<{color}>{pretty_name}</{color}>] " + "[{level}] {message}"
        loggers = {
            "handlers": [
                {
                    "level": os.environ.get("LOGGER_LEVEL", "INFO"),
                    "sink": sys.stderr,
                    "format": logger_format,
                    "colorize": True,
                    "backtrace": True,
                    "diagnose": True,
                },
            ],
        }
        logger.configure(**loggers)
        logger.log_to_file(
            filename=pretty_name,
            folder=settings.BASE_FOLDER / "logs" / "celery" / pretty_name,
            format="[{time:YYYY-MM-DD HH:mm:ss,SSS}] [{level}] <level>{message}</level>",
            level="TRACE",
        )


@tasks.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs) -> None:  # noqa: ARG001 # pylint: disable=unused-argument
    if os.environ.get("AUTOMATIC_TASKS_ENABLED") != "1":
        return

    sender.add_periodic_task(60.0, monitor_sockpuppets.s())
    sender.add_periodic_task(60.0 * 5, fix_vandalism.s())

    sender.add_periodic_task(crontab(minute="0", hour="6,20"), create_artist_tags.s())
    sender.add_periodic_task(crontab(minute="0", hour="9-18"), create_artist_tags.s())
    sender.add_periodic_task(crontab(minute="9", hour="17"), _tag_paid_rewards_on_gelbooru.s())


@tasks.task(base=CustomCeleryTask)
def monitor_sockpuppets() -> None:
    SockpuppetDetector(mode="production").detect_and_post()
    rename_socks()
    delete_feedbacks()


@tasks.task(base=CustomCeleryTask)
def create_artist_tags() -> None:
    exceptions = []
    for search in [
        ["pixiv:any"],
        ["(source:*weibo.com/* or source:*weibo.cn/*)", "-official_art"],
        ["source:*lofter.com/*"],
    ]:
        try:
            add_artists_to_posts(search=search)
        except Exception as e:
            e.add_note(f"On search: {search}")
            exceptions.append(e)
    if exceptions:
        raise exceptions[0]


@tasks.task(base=CustomCeleryTask)
def _tag_paid_rewards_on_gelbooru() -> None:
    tag_paid_rewards_on_gelbooru(mode="latest")


@tasks.task(base=CustomCeleryTask)
def fix_vandalism() -> None:
    post_id = 5019055
    posts = danbooru_api.posts(tags=[f"id:{post_id}", "artistic_error"])
    if not posts:
        logger.info(f"Fixing vandalism on post {post_id}")
        data = {
            "post": {
                "tag_string": "artistic_error",
                "old_tag_string": "",
            },
        }
        danbooru_api.danbooru_request("PUT", f"posts/{post_id}.json", json=data)
