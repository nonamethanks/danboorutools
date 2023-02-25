import re
from typing import Any, Iterable


def assert_equal(lhv: Any, rhv: Any) -> None:  # noqa: ANN401 # SHUT THE FUCK UP
    # ward is a piece of shit that won't pretty-print asserts inside an import, so these have to be used
    # the alternative is killing myself while trying to make py-fucking-test work
    assert lhv == rhv


def assert_isinstance(lhv: Any, rhv: type) -> None:  # noqa: ANN401
    assert isinstance(lhv, rhv)


def assert_in(lhv: Any, rhv: Iterable) -> None:  # noqa: ANN401
    assert lhv in rhv


def assert_match_in(lhv: str, rhv: Any) -> None:  # noqa: ANN401
    assert any(re.search(lhv, found_asset) for found_asset in rhv)


def assert_gte(lhv: Any, rhv: Any) -> None:  # noqa: ANN401
    assert lhv >= rhv
