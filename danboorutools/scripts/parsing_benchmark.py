import time
from typing import Callable

import click
from line_profiler import LineProfiler

from danboorutools import logger
from danboorutools.logical.parsers import ParsableUrl, UrlParser, parsers
from danboorutools.models.url import Url  # , known_url_types
from danboorutools.util.system import PersistentValue

log_file = logger.log_to_file()


@click.command()
@click.option("--times", type=int, default=0)
@click.option("--resume", is_flag=True, default=False)
@logger.catch(reraise=True)
def main(times: int = 0, resume: bool = False) -> None:

    test_set = prepare_test_set(times)
    logger.info(f"Testing URL parsing {len(test_set)} times.")

    do_benchmark(test_set, resume)


def prepare_test_set(times: int) -> list[str]:
    logger.info("Loading data...")
    logger.info("Loading artist urls...")
    with open("data/artist_urls.txt", encoding="utf-8") as myf:
        # TODO: add script to update this and the below from bq
        # https://github.com/danbooru/danbooru/issues/5440 this needs to be fixed first
        test_set = [line.strip().strip("\"") for line in myf if line.strip()]
    logger.info("Artist urls loaded.")
    logger.info("Loading sources...")
    with open("data/sources.txt", encoding="utf-8") as myf:
        test_set += [line.strip().strip("\"") for line in myf if line.strip()]
    logger.info("Sources loaded.")

    if times:
        test_set = test_set[:times]
    return test_set

    # TODO: daily bot that validates all new urls and sends me an email with the bad ones


def do_benchmark(test_set: list[str], resume: bool) -> None:
    profiler = LineProfiler()
    parse_wrapper = prepare_profiler(profiler)
    start = time.time()

    last_fail = PersistentValue("PARSING_BENCHMARK_LAST_FAIL", 0)
    if not resume:
        last_fail.delete()
    elif last_fail.value > 0:
        logger.info(f"Resuming from {last_fail.value - 20:_}.")

    for index, url_string in enumerate(test_set):
        if resume and index < last_fail.value - 20:  # little wiggle room for deleting invalid sources from the files
            continue
        if index % 100_000 == 0:
            logger.info(f"At url {index:_}, {int(time.time() - start)}s elapsed.")
            last_fail.value = index
        try:
            parse_wrapper(url_string)
        except (Exception, KeyboardInterrupt) as e:
            e.add_note(f"At url {index:_} of {len(test_set):_}.")
            last_fail.value = index
            raise

    profiler.print_stats()

    with log_file.open("a+", encoding="utf-8") as log_file_obj:
        profiler.print_stats(stream=log_file_obj)

    last_fail.delete()


def prepare_profiler(profiler: LineProfiler) -> Callable:
    for parser_type in parsers.values():
        try:
            profiler.add_function(parser_type.match_url)
        except ValueError:
            pass
        for method in dir(parser_type):
            if method.startswith("_match"):
                profiler.add_function(getattr(parser_type, method))

    profiler.add_function(UrlParser.parse.__wrapped__)
    profiler.add_function(ParsableUrl.url_data.func)  # type: ignore[attr-defined]
    parse_wrapper = profiler(Url.parse)
    return parse_wrapper
