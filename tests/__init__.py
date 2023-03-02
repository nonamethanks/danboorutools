import re
from typing import Any, Iterable

from ward.expect import Comparison, TestAssertionFailure, _prev_frame


def assert_equal(lhs_val: Any, rhs_val: Any) -> None:  # noqa: ANN401 # SHUT THE FUCK UP
    # ward is a piece of shit that won't pretty-print asserts inside an import, so these have to be used
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


def assert_isinstance(lhs_val: Any, rhs_val: type) -> None:  # noqa: ANN401
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


def assert_in(lhs_val: Any, rhs_val: Iterable) -> None:  # noqa: ANN401
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


def assert_match_in(lhs_val: str | re.Pattern[str], rhs_val: Any) -> None:  # noqa: ANN401
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


def assert_gte(lhs_val: Any, rhs_val: Any) -> None:  # noqa: ANN401
    try:
        assert lhs_val in rhs_val
    except AssertionError as e:
        raise TestAssertionFailure(
            f"{lhs_val} < {rhs_val}",
            lhs=lhs_val,
            rhs=rhs_val,
            error_line=_prev_frame().f_lineno,
            operator=Comparison.GreaterThanEqualTo,
            assert_msg=str(e)
        ) from e
