
from datetime import datetime
from typing import Any, Callable, Literal, Sequence, TypeVar

from pytz import UTC
from ward import expect

from danboorutools.util.time import datetime_from_string

Func = TypeVar("Func", bound=Callable)


class TestFailure(Exception):
    pass


def normalize_values(lhs_value: Any, rhs_value: Any) -> tuple[Any, Any]:  # noqa: ANN401

    if isinstance(lhs_value, datetime) and not isinstance(rhs_value, datetime):
        rhs_value = datetime_from_string(rhs_value)
    elif isinstance(rhs_value, datetime) and not isinstance(lhs_value, datetime):
        lhs_value = datetime_from_string(lhs_value)

    if isinstance(lhs_value, datetime) and not lhs_value.tzinfo:
        lhs_value = lhs_value.replace(tzinfo=UTC)
    if isinstance(rhs_value, datetime) and not rhs_value.tzinfo:
        rhs_value = rhs_value.replace(tzinfo=UTC)

    return lhs_value, rhs_value


def assert_equal(lhs_value: Any, rhs_value: Any) -> None:  # noqa: ANN401
    lhs_value, rhs_value = normalize_values(lhs_value, rhs_value)

    message = f"Expected '{lhs_value}' to be equal to '{rhs_value}'."
    try:
        expect.assert_equal(lhs_value, rhs_value, message)
    except expect.TestAssertionFailure as e:
        raise TestFailure(e.message) from e


def assert_is_instance(lhs_value: object, rhs_value: type) -> None:
    message = f"Expected '{lhs_value}' to be instance of {rhs_value}"
    try:
        expect.assert_is(isinstance(lhs_value, rhs_value), True, message)
    except expect.TestAssertionFailure as e:
        raise TestFailure(e.message) from e


def assert_comparison(lhs_value: int | float | datetime | Sequence,
                      operator: Literal[">=", "<=", ">", "<"],
                      rhs_value: int | float | datetime | Sequence
                      ) -> None:
    lhs_value, rhs_value = normalize_values(lhs_value, rhs_value)

    if isinstance(lhs_value, list):
        lhs_value = len(lhs_value)
        message = f"Expected len({lhs_value})"
    else:
        message = f"Expected {lhs_value}"

    message += " to be {operator} than "

    if isinstance(rhs_value, list):
        rhs_value = len(rhs_value)
        message += f"len({rhs_value})"
    else:
        message += f"{rhs_value}"

    try:
        match operator:
            case ">=":
                message = message.replace("{operator}", "greater than or equal to")
                expect.assert_greater_than_equal_to(lhs_value, rhs_value, message)
            case "<=":
                message = message.replace("{operator}", "less than or equal to")
                expect.assert_less_than_equal_to(lhs_value, rhs_value, message)
            case ">":
                message = message.replace("{operator}", "greater than")
                expect.assert_greater_than(lhs_value, rhs_value, message)
            case "<":
                message = message.replace("{operator}", "less than")
                expect.assert_less_than(lhs_value, rhs_value, message)
            case _:
                raise ValueError(operator)
    except expect.TestAssertionFailure as e:
        raise TestFailure(e.message) from e
