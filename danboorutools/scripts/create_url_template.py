# ruff: noqa: E501

from pathlib import Path

import click

from danboorutools import logger
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.util.system import run_external_command

logger.log_to_file()


@click.command()
@click.argument("url", type=str, required=True)
@click.option("--force", "-f", is_flag=True, default=False)
def main(url: str, force: bool = False) -> None:
    create_url_template(url, force=force)


PARSER_TEMPLATE = """
from danboorutools.logical.urls.{module_name} import {class_name_base}ArtistUrl, {class_name_base}ImageUrl, {class_name_base}PostUrl, {class_name_base}Url
from danboorutools.logical.url_parser import ParsableUrl, UrlParser

class {parser_name_base}Parser(UrlParser):{domains_if_dash}
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> {class_name_base}Url | None:
        match parsable_url.url_parts:
            case _,:
                return {class_name_base}ArtistUrl(parsed_url=parsable_url,
                                                  username=username)
            case _:
                return None
"""

EXTRACTOR_TEMPLATE = """
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class {class_name_base}Url(Url):
    pass


class {class_name_base}ArtistUrl(ArtistUrl, {class_name_base}Url):
    username: str


class {class_name_base}PostUrl(PostUrl, {class_name_base}Url):
    post_id: int


class {class_name_base}ImageUrl(PostAssetUrl, {class_name_base}Url):
    ...
"""

TESTS_TEMPLATE = """
from danboorutools.logical.urls.{module_name} import {class_name_base}ArtistUrl, {class_name_base}PostUrl, {class_name_base}ImageUrl
from tests.urls import generate_parsing_suite

urls = {{
    {class_name_base}ArtistUrl: {{
    }},
    {class_name_base}PostUrl: {{
    }},
    {class_name_base}ImageUrl: {{
    }},
}}


generate_parsing_suite(urls)
"""

TESTS_FOLDER = Path("tests/urls")
PARSERS_FOLDER = Path("danboorutools/logical/parsers")
URLS_FOLDER = Path("danboorutools/logical/urls")


def create_url_template(url: str, force: bool = False) -> None:
    parsed = ParsableUrl(url)
    name_base = parsed.domain.removesuffix(f".{parsed.tld}").replace("-", "_")

    parser_filename = PARSERS_FOLDER / f"{name_base}.py"
    url_filename = URLS_FOLDER / f"{name_base}.py"
    tests_filename = TESTS_FOLDER / f"{name_base}_test.py"

    formatted_parser = PARSER_TEMPLATE.format(
        class_name_base=name_base.title(),
        parser_name_base=parsed.domain.title().replace(".", ""),
        module_name=name_base.replace("-", "_"),
        domains_if_dash=f'\n    domains = ["{parsed.domain}"]\n' if "-" in parsed.domain else "",
    ).strip() + "\n"

    formatted_extractor = EXTRACTOR_TEMPLATE.format(class_name_base=name_base.title()).strip() + "\n"

    formatted_tests = TESTS_TEMPLATE.format(
        class_name_base=name_base.title(),
        module_name=name_base.replace("-", "_"),
    ).strip() + "\n"

    if not parser_filename.is_file() or force:
        with parser_filename.open(mode="w+", encoding="utf-8") as _file:
            _file.write(formatted_parser)
    run_external_command(f"code --reuse-window {parser_filename.resolve()}")

    if not url_filename.is_file() or force:
        with url_filename.open(mode="w+", encoding="utf-8") as _file:
            _file.write(formatted_extractor)
    run_external_command(f"code --reuse-window {url_filename.resolve()}")

    if not tests_filename.is_file() or force:
        with tests_filename.open(mode="w+", encoding="utf-8") as _file:
            _file.write(formatted_tests)
    run_external_command(f"code --reuse-window {tests_filename.resolve()}")
