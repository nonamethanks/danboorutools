import logging
import re

import pytest

pytest.register_assert_rewrite("tests.helpers")


def pytest_collection_modifyitems(items, config):
    items = filter(should_perform_test, items)

    added = []
    for item in items:
        module_name = item.module.__name__  # type: str
        if module_name.startswith("tests.urls"):
            domain = module_name.split(".")[-1].removesuffix("_test")
            if domain not in added:
                config.addinivalue_line("markers", domain)
                added += [domain]
            item.add_marker(getattr(pytest.mark, domain))
            function_name = item.function.__name__  # type: str
            if function_name.startswith("test_parsing"):
                item.add_marker(pytest.mark.parsing)
                item._nodeid = re.sub(r"::test_parsing\[(.*)-(.*)-(.*)\]", "::test_parsing::\\3[\\1]", item.nodeid)

            if isinstance(item.parent, pytest.Class):
                item._node_id = re.sub(r"::test_", f"{item.parent.__class__.__name__}::test_", item.nodeid)


def should_perform_test(item) -> bool:  # noqa: PLR0911
    for property_name in ["posts",  "post_count",
                          "asset_count", "assets",
                          "score", "created_at"]:
        if item.name.endswith(f"test_{property_name}") and getattr(item.parent.obj, property_name) is None:
            return False

    return True


logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("pyrate_limiter").setLevel(logging.INFO)
