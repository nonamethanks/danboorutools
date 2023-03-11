from __future__ import annotations

import functools
import json
import random
import re
import weakref
from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from gelidum import freeze
from pydantic import BaseModel as BadBaseModel
from pydantic import PrivateAttr, ValidationError


def random_string(length: int) -> str:
    """Generate a random string of N length."""
    return "".join(random.choice("0123456789ABCDEF") for i in range(length))


def tryint(string: str) -> str | int:
    """Try to convert a string to integer."""
    try:
        return int(string)
    except ValueError:
        return string


Variable = TypeVar("Variable")


def natsort_array(array: Iterable[Variable]) -> list[Variable]:
    """Sort an array of strings naturally."""
    # https://stackoverflow.com/a/4623518/11558993
    return sorted(array, key=lambda key: [tryint(c) for c in re.split("([0-9]+)", str(key))])


#################################


MemoizedFunction = TypeVar("MemoizedFunction", bound=Callable[..., Any])


def memoize(func: MemoizedFunction) -> MemoizedFunction:
    @functools.wraps(func)
    def wrapped_func(self, *args, **kwargs):  # noqa: ANN001,ANN202
        self_weak = weakref.ref(self)

        @functools.wraps(func)
        @functools.lru_cache
        def cached_method(*args, **kwargs):  # noqa: ANN202
            return func(self_weak(), *args, **kwargs)

        @functools.wraps(cached_method)
        def frozen_method(*args, **kwargs):  # noqa: ANN202
            return cached_method(*freeze(args), **freeze(kwargs))

        setattr(self, func.__name__, frozen_method)

        return frozen_method(*args, **kwargs)

    return wrapped_func  # type: ignore[return-value]

#################################


def class_name_to_string(klass: type, separator: str = "_") -> str:
    class_name = klass.__name__
    return class_name[0].lower() + "".join(f"{separator}{char.lower()}" if char.isupper() else char for char in class_name[1:])


all_urls_pattern = re.compile(
    r'((?:\bhttp|https)(?::\/{2}[\w]+)(?:[\/|\.]?)(?:[^\s<>\uff08\uff09\u3011\u3000"\[\]\(\)]*))',
    re.IGNORECASE | re.ASCII,
)
images_pattern = re.compile(r".*(jpg|jpeg|gif|png)$", re.IGNORECASE)


def extract_urls_from_string(string: str, blacklist_images: bool = True) -> list[str]:
    found = [
        u.strip().strip("/?{}()\',.\" ")
        for u in all_urls_pattern.findall(string)
        if re.match(r".+\..+", u)
    ]

    if not blacklist_images:
        return found
    urls = [u for u in found if not images_pattern.search(u.strip())]
    return list(dict.fromkeys(urls))


class BaseModel(BadBaseModel):
    _raw_data: dict = PrivateAttr()

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            e.add_note(f"Failed to validate:\n {json.dumps(data, indent=4)}\n")
            raise
        else:
            self._raw_data = data
