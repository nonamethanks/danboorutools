

import random
import time
from pathlib import Path

import click

from danboorutools import logger
from danboorutools.models.url import UnknownUrl, Url, known_url_types
from danboorutools.util.misc import get_url_domain

logger.add(f"logs/scripts/{Path(__file__).stem}/" + "{time}.log", retention="7 days")


@click.command()
@click.argument("times", type=int, default=10000)
def main(times: int) -> None:
    print(f"Testing URL parsing {times} times.")

    test_cases = [test_case for url_type in known_url_types for test_case in url_type.test_cases]
    test_set = [random.choice(test_cases) for i in range(times)]

    start = time.time()
    for url_string in test_set:
        uncached_parsing(url_string)
    end = time.time() - start
    print(f"Uncached Parsing: {end}s.")

    start = time.time()
    for url_string in test_set:
        Url.parse(url_string)
    end = time.time() - start
    print(f"Cached Parsing: {end}s.")


def uncached_parsing(url) -> Url:
    url_domain = get_url_domain(url)
    for url_strategy in known_url_types:
        if url_domain not in url_strategy.domains:
            continue
        if any(excluded_path in url for excluded_path in url_strategy.excluded_paths):
            continue
        if match := url_strategy.pattern.match(url):
            return url_strategy(url, match.groupdict())

    return UnknownUrl(url, {})
