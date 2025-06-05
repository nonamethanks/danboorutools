import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import click
from line_profiler import LineProfiler

from danboorutools import logger, settings
from danboorutools.logical.progress_tracker import ProgressTracker
from danboorutools.logical.url_parser import ParsableUrl, UrlParser, parsers
from danboorutools.models.url import UnknownUrl, UnsupportedUrl, Url, UselessUrl
from danboorutools.util.bigquery import execute_bigquery_query

log_file = logger.log_to_file()

ARTIST_URLS_FILE = Path(settings.BASE_FOLDER / "data" / "artist_urls.txt")
SOURCE_URLS_FILE = Path(settings.BASE_FOLDER / "data" / "sources.txt")


@click.command()
@click.option("--times", type=int, default=0)
@click.option("--domain", type=str, default=None)
@click.option("--resume", is_flag=True, default=False)
@click.option("--unparsed", is_flag=True, default=False)
@click.option("--update", is_flag=True, default=False)
def main(times: int = 0, resume: bool = False, unparsed: bool = False, update: bool = False, domain: str | None = None) -> None:
    if update:
        update_urls()
        return

    if domain:
        domain = Url.parse(domain).parsed_url.domain
        logger.info(f"Parsing for domain {domain}")

    test_set = prepare_test_set(times, domain)

    if unparsed:
        print_unparsed(test_set)

    else:
        logger.info(f"Testing URL parsing {len(test_set)} times.")

        bulk_parse(test_set, resume, log_urls=domain is not None)


def update_urls() -> None:
    logger.info("Fetching artist urls.")

    artist_query = "SELECT artist_id, url FROM `danbooru1.danbooru_public.artist_urls` "
    artist_query_result = execute_bigquery_query(artist_query)
    artist_urls = tuple((f"https://danbooru.donmai.us/artists/{row.artist_id}", row.url) for row in artist_query_result)
    logger.info(f"Found {len(artist_urls)} artist urls.")
    ARTIST_URLS_FILE.write_text("\n".join(",".join(map(str, a)) for a in artist_urls), encoding="utf-8")

    source_query = "SELECT id, source FROM `danbooru1.danbooru_public.posts` where source like 'http%'"
    source_query_result = execute_bigquery_query(source_query)
    logger.info("Fetching source urls.")
    source_urls: list[tuple[str, str]] = []
    for index, row in enumerate(source_query_result):
        if index % 200_000 == 0:
            logger.info(f"At {index:_}")
        if not row.source.startswith(("http://", "https://")):
            continue
        source_urls += [(f"https://danbooru.donmai.us/posts/{row.id}", row.source)]
    logger.info(f"Found {len(source_urls)} source urls.")
    SOURCE_URLS_FILE.write_text("\n".join(",".join(map(str, s)) for s in source_urls), encoding="utf-8")


def print_unparsed(test_set: list[list[str]]) -> None:
    unparsed_domains = []
    for index, (_resource_url, url_string) in enumerate(test_set):
        if index % 200_000 == 0:
            logger.info(f"Computing url {index:_} of {len(test_set):_}...")
        parsed_url = ParsableUrl(url_string)
        if parsed_url.domain not in parsers:
            unparsed_domains.append(parsed_url.domain)
    domains = Counter(unparsed_domains)
    logger.info("Most common unparsed domains:")
    for index, (domain, number) in enumerate(domains.most_common(20)):
        logger.info(f"{index + 1:2d}: {domain} ({number})")


def prepare_test_set(times: int, domain: str | None) -> list[list[str]]:
    logger.info("Loading data...")
    with ARTIST_URLS_FILE.open(encoding="utf-8") as myf:
        test_set = [line.strip().strip('"').split(",") for line in myf if line.strip()]
    logger.info("Loading sources...")
    with SOURCE_URLS_FILE.open(encoding="utf-8") as myf:
        test_set += [line.strip().strip('"').split(",") for line in myf if line.strip()]
    logger.info("Sources loaded.")

    if domain:
        test_set = [t for t in test_set if f".{domain}" in t[1] or f"//{domain}" in t[1]]

    if times:
        test_set = test_set[:times]

    logger.info(f"{len(test_set)} total urls loaded.")
    return test_set

    # TODO: daily bot that validates all new urls and sends me an email with the bad ones


def bulk_parse(test_set: list[list[str]], resume: bool, log_urls: bool = False) -> None:
    profiler = LineProfiler()
    parse_wrapper = prepare_profiler(profiler)
    start = time.time()

    last_fail = ProgressTracker("PARSING_BENCHMARK_LAST_FAIL", 0)
    if not resume:
        del last_fail.value
    elif last_fail.value > 0:
        logger.info(f"Resuming from {last_fail.value - 20:_}.")

    results: list[tuple[str, Url]] = []
    for index, (resource_url, url_string) in enumerate(test_set):
        if resume and index < last_fail.value - 20:  # little wiggle room for deleting invalid sources from the files
            continue
        if index % 100_000 == 0:
            logger.info(f"At url {index:_}, {int(time.time() - start)}s elapsed.")
            last_fail.value = index
        try:
            results.append((resource_url, parse_wrapper(url_string)))
        except (Exception, KeyboardInterrupt) as e:
            e.add_note(f"At url {index:_} of {len(test_set):_}, found on {resource_url}.")
            last_fail.value = index
            raise

    # profiler.print_stats()
    if not results:
        raise ValueError("No results found.")

    with log_file.open("a+", encoding="utf-8") as log_file_obj:
        profiler.print_stats(stream=log_file_obj)

    logger.info("Done.")

    if log_urls:
        results.sort(key=lambda x: (isinstance(x[1], (UnknownUrl | UnsupportedUrl | UselessUrl)),
                                    x[1].__class__.__name__,
                                    x[1].parsed_url.subdomain,
                                    len(x[1].parsed_url.url_parts),
                                    x[1].parsed_url.path))

        logger.info("")
        logger.info("#### PARSING RESULTS ####")
        logger.info("")

        padding = len(max(results, key=lambda x: len(x[1].__class__.__name__))[1].__class__.__name__) + 5
        for resource_url, url in results:
            logger.info(
                f"{url.__class__.__name__:<{padding}}" + url.parsed_url.raw_url.replace("http:", "https:") + f" - {resource_url}",
            )
        logger.info("#######################")
        logger.info(f"Total: {len(results)} urls.")
        logger.info("#######################")
        logger.info("")

    logger.info(f"Results available at {log_file}.")

    del last_fail.value


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
    profiler.add_function(UrlParser._parse)
    profiler.add_function(ParsableUrl.url_data.func)  # type: ignore[attr-defined]
    parse_wrapper = profiler(Url.parse)
    return parse_wrapper
