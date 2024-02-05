from __future__ import annotations

import datetime
import inspect
from functools import cached_property, lru_cache
from importlib import import_module
from typing import TypeVar

from danboorutools import settings
from danboorutools.logical.sessions import Session
from danboorutools.models.has_posts import HasPosts

feeds: list[type[Feed]] = []


class Feed(HasPosts):
    session = Session()

    quit_early_page = 3
    max_post_age = datetime.timedelta(days=14)
    first_page_must_have_posts = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"

    @property
    def pathable_name(self) -> str:
        return f"Feed.{self.__class__.__name__}"

    @staticmethod
    @lru_cache
    def get_all_feeds() -> list[type[Feed]]:
        feed_folder = settings.BASE_FOLDER / "danboorutools" / "logical" / "feeds"
        for _file in feed_folder.glob("*.py"):
            if "__" not in _file.stem:
                import_module(f"danboorutools.logical.feeds.{_file.stem}")
        return feeds

    def __init_subclass__(cls, *args, **kwargs) -> None:
        if cls.__name__.startswith("_"):
            return

        if inspect.getfile(cls) == __file__:
            return

        feeds.append(cls)

    @cached_property
    def site_name(self) -> str:
        current_module = self.__module__
        subfolder, submodule = current_module.rsplit(".", 1)
        if not subfolder.endswith("danboorutools.logical.feeds"):
            raise NotImplementedError("Site name unknown")
        if not submodule:
            raise NotImplementedError("Site name unknown")
        return submodule

    @property
    def normalized_url(self) -> str:
        raise NotImplementedError(self)


PostDataVar = TypeVar("PostDataVar")
