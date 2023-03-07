import inspect
import re
from pathlib import Path
from typing import Any, Callable, Iterable

from ward import _testing
from ward.expect import Comparison, TestAssertionFailure, _prev_frame
from ward.models import CollectionMetadata, XfailMarker


def assert_equal(lhs_val: Any, rhs_val: Any) -> None:
    # ward won't pretty-print asserts inside an import, so this is a mandatory trick to have legible output
    # the alternative is killing myself while trying to make py-fucking-test work
    try:
        assert lhs_val == rhs_val
    except AssertionError as e:
        raise TestAssertionFailure(
            f"{lhs_val} does not equal {rhs_val}",
            lhs=lhs_val,
            rhs=rhs_val,
            error_line=_prev_frame().f_lineno,
            operator=Comparison.Equals,
            assert_msg=str(e)
        ) from e


def assert_isinstance(lhs_val: Any, rhs_val: type) -> None:
    try:
        assert isinstance(lhs_val, rhs_val)
    except AssertionError as e:
        raise TestAssertionFailure(
            f"{lhs_val} is instance of {type(lhs_val)}, not of {rhs_val}",
            lhs=type(lhs_val),
            rhs=rhs_val,
            error_line=_prev_frame().f_lineno,
            operator=Comparison.Equals,
            assert_msg=str(lhs_val)
        ) from e


def assert_in(lhs_val: Any, rhs_val: Iterable) -> None:
    try:
        assert lhs_val in rhs_val
    except AssertionError as e:
        raise TestAssertionFailure(
            f"{lhs_val} is not in {rhs_val}",
            lhs=lhs_val,
            rhs=rhs_val,
            error_line=_prev_frame().f_lineno,
            operator=Comparison.In,
            assert_msg=str(e)
        ) from e


def assert_match_in(lhs_val: str | re.Pattern[str], rhs_val: Any) -> None:
    if isinstance(lhs_val, str):
        lhs_val = re.compile(lhs_val)

    try:
        assert any(re.search(lhs_val, element) for element in rhs_val)
    except AssertionError as e:
        raise TestAssertionFailure(
            f"Pattern {lhs_val} didn't match any element in {rhs_val}",
            lhs=lhs_val,
            rhs=rhs_val,
            error_line=_prev_frame().f_lineno,
            operator=Comparison.In,
            assert_msg=str(e)
        ) from e


def assert_gte(lhs_val: Any, rhs_val: Any) -> None:
    try:
        assert lhs_val >= rhs_val
    except AssertionError as e:
        raise TestAssertionFailure(
            f"{lhs_val} < {rhs_val}",
            lhs=lhs_val,
            rhs=rhs_val,
            error_line=_prev_frame().f_lineno,
            operator=Comparison.GreaterThanEqualTo,
            assert_msg=str(e)
        ) from e


def generate_ward_test(method: Callable, /, description: str, tags: list[str], expected_failure: bool = False) -> None:
    caller = inspect.stack()[2]
    abs_path = Path(caller.filename).resolve()
    method.ward_meta = CollectionMetadata(  # type: ignore[attr-defined]
        description=description,
        tags=tags,
        path=abs_path,
    )
    if expected_failure:
        method.ward_meta.marker = XfailMarker()  # type: ignore[attr-defined]

    _testing.COLLECTED_TESTS[abs_path].append(method)
