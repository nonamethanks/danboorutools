

import random
import time
from pathlib import Path

import click
from line_profiler import LineProfiler

from danboorutools import logger
from danboorutools.models.url import Url, known_url_types

logger.add(f"logs/scripts/{Path(__file__).stem}/" + "{time}.log", retention="7 days")


@click.command()
@click.argument("times", type=int, default=10_000)
def main(times: int) -> None:
    print(f"Testing URL parsing {times} times.")

    test_cases = [test_case for url_type in known_url_types for test_case in url_type.test_cases]
    test_set = [random.choice(test_cases) for i in range(times)]

    profiler = LineProfiler()
    parse_wrapper = profiler(Url._parse)
    for url_string in test_set:
        parse_wrapper(url_string)
    profiler.print_stats()
