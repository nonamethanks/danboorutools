import inspect
import logging
import re

import pytest

pytest.register_assert_rewrite("tests.helpers")


def pytest_collection_modifyitems(items, config):
    added = []
    for item in items:
        module_name = item.module.__name__  # type: str
        if module_name.startswith("tests.urls"):
            domain = item.parent.name.removesuffix("_test.py")
            if domain not in added:
                config.addinivalue_line("markers", domain)
                added += [domain]
            item.add_marker(getattr(pytest.mark, domain))

            validate_function_name(item)
            rename_item(item)


url_types = ["artist", "gallery", "info", "redirect", "post"]


def validate_function_name(item) -> None:
    function_name = item.function.__name__  # type: str
    if function_name.startswith("test_parsing"):
        item.add_marker(pytest.mark.parsing)
    elif function_name.startswith(tuple(f"test_{url_type}_url" for url_type in url_types)):
        for test_type in url_types:
            if function_name.startswith(f"test_{test_type}_url"):
                break
        else:
            raise NotImplementedError(function_name)

        source = inspect.getsource(item.function)
        string = re.search(r'url_string="(.*?)"', source)
        url_type = re.search(r"url_type=(?:\w+\.)?(\w+),?", source)
        assert string, item.nodeid
        assert url_type, item.nodeid
        item._nodeid = f"{item.nodeid}::{test_type}::{url_type.groups()[0]}[{string.groups()[0]}]"
        item.add_marker(getattr(pytest.mark, test_type))
        item.add_marker(pytest.mark.scraping)
    else:
        raise NotImplementedError(function_name)


def rename_item(item):
    function_name = item.function.__name__
    if function_name.startswith("test_parsing"):
        item._nodeid = re.sub(r"::test_parsing\[(.*)-(.*)-(.*)\]", "::test_parsing::\\3[\\1]", item.nodeid)


logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("pyrate_limiter").setLevel(logging.INFO)
