import ast
import importlib
from pathlib import Path

from danboorutools.models.base_url import BaseUrl

known_urls: list[type[BaseUrl]] = []
for url_file_path in Path(__file__).parent.glob("*.py"):
    if url_file_path.stem.startswith("_"):
        continue

    parsed_file = ast.parse(url_file_path.read_text())
    for node in parsed_file.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if any(base.id in ["BaseUrl", "Session"] for base in node.bases if isinstance(base, ast.Name)):
            continue
        module = importlib.import_module(f"danboorutools.logical.extractors.{url_file_path.stem}")

        klass = getattr(module, node.name)
        if not issubclass(klass, BaseUrl):
            continue

        if not hasattr(klass, "patterns"):
            continue

        known_urls.append(klass)


class UnknownUrl(BaseUrl):
    pass


def parse_url(url: str) -> BaseUrl:
    for url_strategy in known_urls:
        if url_instance := url_strategy.match(url):
            return url_instance

    return UnknownUrl(url, "", {})
