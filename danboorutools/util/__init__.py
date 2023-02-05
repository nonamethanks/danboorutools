import random
from typing import Iterable, TypeVar

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
        url_data = extractor.extract_from_url(url)  # pylint: disable=no-member  # XXX false positive
    except ValueError as e:
        if ": no scheme" in str(e):
            url_data = extractor.extract(url)
        else:
            raise
    url_domain = url_data["domain"] + "." + url_data["suffix"]
    return url_domain
