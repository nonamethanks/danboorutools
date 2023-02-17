from __future__ import annotations

import functools
import random
import re
import weakref
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Callable, Generic, Iterable, TypeVar, overload

from pydomainextractor import DomainExtractor


def random_string(length: int) -> str:
    """Generate a random string of N length."""
    return "".join(random.choice('0123456789ABCDEF') for i in range(length))


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
    return sorted(array, key=lambda key: [tryint(c) for c in re.split('([0-9]+)', str(key))])


domain_extractor = DomainExtractor()


@lru_cache
def get_url_data(url: str) -> dict[str, str]:
    try:
        url_data = domain_extractor.extract_from_url(url)
    except ValueError as e:
        if ": no scheme" in str(e):
            url_data = domain_extractor.extract(url)
        else:
            raise
    url_data["full_domain"] = url_data["domain"] + "." + url_data["suffix"]
    return url_data


MemoizedFunction = TypeVar("MemoizedFunction", bound=Callable[..., Any])


def memoize(func: MemoizedFunction) -> MemoizedFunction:
    @functools.wraps(func)
    def wrapped_func(self, *args, **kwargs):  # noqa
        self_weak = weakref.ref(self)

        @functools.wraps(func)
        @functools.lru_cache()
        def cached_method(*args, **kwargs):  # noqa
            return func(self_weak(), *args, **kwargs)
        setattr(self, func.__name__, cached_method)
        return cached_method(*args, **kwargs)

    return wrapped_func  # type: ignore[return-value]


if TYPE_CHECKING:
    import collections.abc as cx


SettableValue = TypeVar("SettableValue")


class settable_property(property, Generic[SettableValue]):  # pylint: disable=invalid-name

    fget: cx.Callable[[Any], SettableValue]

    def __init__(self, fget: cx.Callable[[Any], SettableValue], /) -> None:
        super().__init__(fget)
        self.private_name = "_" + fget.__name__
        self.public_name = fget.__name__

    if TYPE_CHECKING:
        @overload  # type: ignore[override, no-overload-impl]
        def __get__(self, instance: None, Class: type, /) -> settable_property[SettableValue]:
            """ Retrieving a property from on a class retrieves the property object (`settable_property[SettableValue]`) """

        @overload
        def __get__(self, instance: object, Class: type, /) -> SettableValue:
            """ Retrieving a property from the instance retrieves the value """

    def __get__(self, instance, Class):
        if instance is None:
            return self
        if not hasattr(instance, self.private_name) or getattr(instance, self.private_name) is None:
            init_value = self.fget(instance)
            self.__set__(instance, init_value)
        return getattr(instance, self.private_name)

    def __set__(self, instance: object, value: SettableValue) -> None:  # noqa: ANN401
        """
        Type-safe setter method. Grabs the name of the function first decorated with
        `@settable_property`, then calls `setattr` on the given value with an attribute name of
        '_<function name>'.
        """

        setattr(instance, self.private_name, value)

    def __delete__(self, instance: object) -> None:
        if instance is None:
            return

        try:
            delattr(instance, self.private_name)
        except AttributeError:
            pass


def class_name_to_string(klass: type, separator: str = "_") -> str:
    class_name = klass.__name__
    return class_name[0].lower() + "".join(f"{separator}{char.lower()}" if char.isupper() else char for char in class_name[1:])
