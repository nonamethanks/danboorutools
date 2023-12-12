# ruff: noqa: E501

import click

from danboorutools import logger, settings
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.util.system import run_external_command

logger.log_to_file()


@click.command()
@click.argument("url", type=str, required=True)
@click.option("--force", "-f", is_flag=True, default=False)
def main(url: str, force: bool = False) -> None:
    create_url_template(url, force=force)


PARSER_TEMPLATE = """
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.{module_name} import {class_name_base}ArtistUrl, {class_name_base}ImageUrl, {class_name_base}PostUrl, {class_name_base}Url

class {parser_name_base}Parser(UrlParser):{domains_if_bad_chars}
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
from danboorutools.logical.sessions.{module_name} import {class_name_base}ArtistData, {class_name_base}Session
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class {class_name_base}Url(Url):
    session = {class_name_base}Session()


class {class_name_base}ArtistUrl(ArtistUrl, {class_name_base}Url):
    username: str

    @property
    def artist_data(self) -> {class_name_base}ArtistData:
        return self.session.artist_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        raise NotImplementedError
        return [self.artist_data.name]

    @property
    def secondary_names(self) -> list[str]:
        raise NotImplementedError
        return [self.username]

    @property
    def related(self) -> list[Url]:
        raise NotImplementedError
        return self.artist_data.related_urls


class {class_name_base}PostUrl(PostUrl, {class_name_base}Url):
    post_id: int


class {class_name_base}ImageUrl(PostAssetUrl, {class_name_base}Url):
    ...
"""

SESSION_TEMPLATE = """
from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class {class_name_base}Session(Session):
    def artist_data(self, username: str) -> {class_name_base}ArtistData:
        artist_data = self.get_json(f"")
        return {class_name_base}ArtistData(**artist_data)


class {class_name_base}ArtistData(BaseModel):
    name: str

    @property
    def related_urls(self) -> list[Url]:
        raise NotImplementedError
"""

TESTS_TEMPLATE = """
import pytest

from danboorutools.logical.urls.{module_name} import {class_name_base}ArtistUrl, {class_name_base}ImageUrl, {class_name_base}PostUrl
from tests.helpers.parsing import generate_parsing_test

urls = {{
    {class_name_base}ArtistUrl: {{
        "{original_url}": "{original_url}",
    }},
    {class_name_base}PostUrl: {{
    }},
    {class_name_base}ImageUrl: {{
    }},
}}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class Test{class_name_base}ArtistUrl(_TestArtistUrl):
    url_string = "{original_url}"
    url_type = {class_name_base}ArtistUrl
    url_properties = dict(username=)
    primary_names = []
    secondary_names = []
    related = []

"""

BASE_FOLDER = settings.BASE_FOLDER / "danboorutools"
TESTS_FOLDER = settings.BASE_FOLDER / "tests" / "urls"
PARSERS_FOLDER = BASE_FOLDER/"logical"/"parsers"
URLS_FOLDER = BASE_FOLDER / "logical"/"urls"
SESSION_FOLDER = BASE_FOLDER/"logical"/"sessions"


def classize(string: str) -> str:
    return string.title().replace(".", "").replace("-", "")


def create_url_template(url: str, force: bool = False) -> None:
    parsed = ParsableUrl(url)
    name_base = parsed.domain.removesuffix(f".{parsed.tld}")

    parser_filename = PARSERS_FOLDER / f"{name_base.replace('-', '_')}.py"
    url_filename = URLS_FOLDER / f"{name_base.replace('-', '_')}.py"
    session_filename = SESSION_FOLDER / f"{name_base.replace('-', '_')}.py"
    tests_filename = TESTS_FOLDER / f"{name_base.replace('-', '_')}_test.py"

    formatted_parser = PARSER_TEMPLATE.format(
        class_name_base=classize(name_base),
        parser_name_base=classize(parsed.domain),
        module_name=name_base.replace("-", "_"),
        domains_if_bad_chars=f'\n    domains = ["{parsed.domain}"]\n' if not name_base.isalnum() else "",
    ).strip() + "\n"

    formatted_extractor = EXTRACTOR_TEMPLATE.format(
        class_name_base=classize(name_base),
        module_name=name_base.replace("-", "_"),
    ).strip() + "\n"

    formatted_session = SESSION_TEMPLATE.format(
        class_name_base=classize(name_base),
        module_name=name_base.replace("-", "_"),
    ).strip() + "\n"

    formatted_tests = TESTS_TEMPLATE.format(
        class_name_base=classize(name_base),
        module_name=name_base.replace("-", "_"),
        original_url=url,
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

    if not tests_filename.is_file() or force:
        with tests_filename.open(mode="w+", encoding="utf-8") as _file:
            _file.write(formatted_tests)
    run_external_command(f"code --reuse-window {tests_filename.resolve()}")

    if not session_filename.is_file() or force:
        with session_filename.open(mode="w+", encoding="utf-8") as _file:
            _file.write(formatted_session)
    run_external_command(f"code --reuse-window {session_filename.resolve()}")
