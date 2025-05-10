from __future__ import annotations

import pickle
import random
import re
from typing import TYPE_CHECKING, Any, TypeVar, dataclass_transform

from pydantic import BaseModel as BadBaseModel
from pydantic import PrivateAttr, ValidationError

from danboorutools import settings
from danboorutools.exceptions import NoCookiesForDomainError

if TYPE_CHECKING:
    from collections.abc import Iterable


def random_string(length: int) -> str:
    """Generate a random string of N length."""
    return "".join(random.choice("0123456789ABCDEF") for i in range(length))


def tryint(string: str) -> str | int:
    """Try to convert a string to integer."""
    try:
        return int(string)
    except ValueError:
        return string


Variable = TypeVar("Variable")


def natsort_array(array: Iterable[Variable]) -> list[Variable]:
    """Sort an array of strings naturally."""
    # https://stackoverflow.com/a/4623518/11558993
    return sorted(array, key=lambda key: [tryint(c) for c in re.split("([0-9]+)", str(key))])


#################################


def class_name_to_string(klass: type, separator: str = "_") -> str:
    class_name = klass.__name__
    return class_name[0].lower() + "".join(f"{separator}{char.lower()}" if char.isupper() else char for char in class_name[1:])


DELIMITERS = r'\s<>\"\[\]\(\)\|｜、，。〈〉《》「」『』【】〔〕〖〗〘〙〚〛）］｝｠｣　…'
all_urls_pattern = re.compile(rf"((?:\bhttp|https)(?::\/{{2}}[\w]+)(?:[\/|\.]?)(?:[^{DELIMITERS}]*))", re.IGNORECASE | re.ASCII)
files_pattern = re.compile(r".*(jpe?g|gif|png|webp|avif|mp4|mkv|webm|swf)$", re.IGNORECASE)


def extract_urls_from_string(string: str, blacklist_images: bool = True) -> list[str]:
    found = [
        u.strip().strip("/?{}()\',.\" ")
        for u in all_urls_pattern.findall(string)
        if re.match(r".+\..+", u)
    ]

    if not blacklist_images:
        return found
    urls = [u for u in found if not files_pattern.search(u.strip())]
    return list(dict.fromkeys(urls))


def remove_indent(string: str) -> str:
    first_line = next(line for line in string.split("\n") if line)
    spaces = 0
    for character in first_line:
        if character == " ":
            spaces += 1
        else:
            break
    if not spaces:
        return string

    return re.sub(rf"\n {"{" + str(spaces) + "}"}", "\n", string.strip(""))


class BaseModel(BadBaseModel):
    _raw_data: dict[str, Any] = PrivateAttr()

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            try:
                values = value_from_validation_error(data, e)
            except KeyError:
                e.add_note(f"Failed to validate the following input:\n>\t{data}\n")
            else:
                e.add_note(f"\n>\t{data}\nFailed to validate the following input:\n>\t{values}\n")
            raise
        else:
            self._raw_data = data


def value_from_validation_error(data: dict, exception: ValidationError) -> dict:
    values = {}
    for error in exception.errors():
        loc = error["loc"]
        value = data
        for field in loc:
            if field == "__root__":
                break
            value = value[field]
        values[".".join([str(location) for location in loc])] = value
    return values


cookie_dir = settings.BASE_FOLDER / "cookies"


def load_cookies_for(domain: str) -> list[dict[str, str]]:
    filename = cookie_dir / f"cookies-{domain}.pkl"
    if not filename.is_file():
        raise NoCookiesForDomainError(domain)

    cookies: list[dict] = pickle.load(filename.open("rb"))  # noqa: S301
    for cookie in cookies:
        if "expiry" in cookie:
            cookie["expires"] = cookie["expiry"]
            del cookie["expiry"]
    return cookies


def save_cookies_for(domain: str, cookies: list[dict[str, str]]) -> None:
    """Save cookies for a domain."""
    filename = cookie_dir / f"cookies-{domain}.pkl"
    cookie_dir.mkdir(exist_ok=True)
    pickle.dump(cookies, filename.open("wb+"))


@dataclass_transform()
class PseudoDataclass(type):
    def __hash__(cls) -> int:
        return random.randint(1, int(1e10))


def base36encode(number: int) -> str:
    """Base36-encode a number."""
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    base36 = ""
    sign = ""

    if number < 0:
        sign = "-"
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, index = divmod(number, len(alphabet))
        base36 = alphabet[index] + base36

    return sign + base36
