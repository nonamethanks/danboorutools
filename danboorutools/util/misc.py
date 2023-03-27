from __future__ import annotations

import functools
import pickle
import random
import re
import sys
import weakref
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, TypeVar

import _testcapi
from gelidum import freeze
from pydantic import BaseModel as BadBaseModel
from pydantic import PrivateAttr, ValidationError

from danboorutools.exceptions import NoCookiesForDomainError


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
            try:
                return func(self_weak(), *args, **kwargs)
            except:
                _type, exception, _traceback = sys.exc_info()
                _testcapi.set_exc_info(_type, exception, _traceback.tb_next)  # type: ignore[union-attr]
                del _type, exception, _traceback
                raise

        @functools.wraps(cached_method)
        def frozen_method(*args, **kwargs):  # noqa: ANN202
            try:
                return cached_method(*freeze(args), **freeze(kwargs))
            except:
                _type, exception, _traceback = sys.exc_info()
                _testcapi.set_exc_info(_type, exception, _traceback.tb_next)  # type: ignore[union-attr]
                del _type, exception, _traceback
                raise

        setattr(self, func.__name__, frozen_method)

        try:
            return frozen_method(*args, **kwargs)
        except:
            _type, exception, _traceback = sys.exc_info()
            _testcapi.set_exc_info(_type, exception, _traceback.tb_next)  # type: ignore[union-attr]
            del _type, exception, _traceback
            raise

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
    _raw_data: dict[str, Any] = PrivateAttr()

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            debug_method = print if in_ipython() else e.add_note  # https://github.com/ipython/ipython/issues/13849
            try:
                values = value_from_validation_error(data, e)
            except KeyError:
                debug_method(f"Failed to validate:\n {data}\n")  # type: ignore[operator]
            else:
                debug_method(f"\n{data}\nFailed to validate:\n{values}\n")  # type: ignore[operator]
            raise
        else:
            self._raw_data = data


def value_from_validation_error(data: dict, exception: ValidationError) -> dict:
    values = {}
    for error in exception.errors():
        loc = error["loc"]
        value = data
        for field in loc:
            if field == "__root__":
                break
            value = value[field]
        values[".".join([str(location) for location in loc])] = value
    return values


def in_ipython() -> bool:
    try:
        get_ipython().__class__.__name__  # type: ignore[name-defined]
    except NameError:
        return False
    else:
        return True


cookie_dir = Path("cookies")


def load_cookies_for(domain: str) -> list[dict[str, str]]:
    filename = cookie_dir / f"cookies-{domain}.pkl"
    try:
        cookies: list[dict] = pickle.load(filename.open("rb"))
    except FileNotFoundError as e:
        raise NoCookiesForDomainError(domain) from e
    for cookie in cookies:
        if "expiry" in cookie:
            cookie["expires"] = cookie["expiry"]
            del cookie["expiry"]
    return cookies


def save_cookies_for(domain: str, cookies: list[dict[str, str]]) -> None:
    """Save cookies for a domain."""
    filename = cookie_dir / f"cookies-{domain}.pkl"
    cookie_dir.mkdir(exist_ok=True)
    pickle.dump(cookies, filename.open("wb+"))
