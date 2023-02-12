from __future__ import annotations

import functools
import random
import weakref
from typing import TYPE_CHECKING, Any, Callable, Generic, Iterable, TypeVar, overload

import regex
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
    return sorted(array, key=lambda key: [tryint(c) for c in regex.split('([0-9]+)', str(key))])


def compile_url(*patterns: str | regex.Pattern[str]) -> regex.Pattern[str]:
    first_pattern = patterns[0] if isinstance(patterns[0], str) else patterns[0].pattern
    to_compile = r"https?:\/\/(?:www\.)?" if not first_pattern.startswith("http") else ""

    for pattern in patterns:
        to_compile += pattern.pattern if isinstance(pattern, regex.Pattern) else pattern

    return regex.compile(to_compile)


extractor = DomainExtractor()


def get_url_domain(url: str) -> str:
    try:
        url_data = extractor.extract_from_url(url)
    except ValueError as e:
        if ": no scheme" in str(e):
            url_data = extractor.extract(url)
        else:
            raise
    url_domain = url_data["domain"] + "." + url_data["suffix"]
    return url_domain


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
        # Type-safe descriptor protocol for property retrieval methods (`__get__`)
        # see https://docs.python.org/3/howto/descriptor.html
        # These are under `typing.TYPE_CHECKING` because we don't need
        # to modify their implementation from `builtins.property`, but
        # just need to add type-safety.
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

    def __set__(self, instance: Any, value: Any) -> None:  # noqa: ANN401
        """
        Type-safe setter method. Grabs the name of the function first decorated with
        `@settable_property`, then calls `setattr` on the given value with an attribute name of
        '_<function name>'.
        """

        setattr(instance, f"_{self.fget.__name__}", value)
