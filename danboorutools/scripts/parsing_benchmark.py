import time
from pathlib import Path

import click
from line_profiler import LineProfiler

from danboorutools import logger
from danboorutools.logical.parsers import ParsableUrl, UrlParser, parsers
from danboorutools.models.url import Url  # , known_url_types

logger.add(f"logs/scripts/{Path(__file__).stem}/" + "{time}.log", retention="7 days")


@click.command()
@click.option("--times", type=int, default=0)
@click.option("--position", type=int, default=0)
def main(times: int = 0, position: int = 0) -> None:

    # url_types = [url_type for group_of_types in known_url_types.values() for url_type in group_of_types]
    # test_cases = [test_case for url_type in url_types for test_case in url_type.test_cases]
    # test_set = [random.choice(test_cases) for i in range(times)]
    with open("data/sources.txt", encoding="utf-8") as myf:  # TODO: add script to update this from bq
        test_set = [line.strip().strip("\"") for line in myf if line.strip()]

    if times:
        test_set = test_set[:times]

    print(f"Testing URL parsing {len(test_set)} times.")
    profiler = LineProfiler()

    for parser_type in parsers.values():
        profiler.add_function(parser_type.match_url)
        for method in dir(parser_type):
            if method.startswith("_match"):
                profiler.add_function(getattr(parser_type, method))

    profiler.add_function(UrlParser.parse.__wrapped__)
    profiler.add_function(ParsableUrl.url_data.func)  # type: ignore[attr-defined]
    parse_wrapper = profiler(Url.parse)
    start = time.time()
    for index, url_string in enumerate(test_set):
        if index < position:
            continue
        if index % 100_000 == 0:
            print(f"At url {index:_}, {int(time.time() - start)}s elapsed.")
        try:
            parse_wrapper(url_string)
        except Exception as e:
            e.add_note(f"At url {index:_} of {len(test_set):_}.")
            raise

    profiler.print_stats()
    # TODO: daily bot that validates all new urls and sends me an email with the bad ones
