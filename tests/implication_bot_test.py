import re

import pytest

from danboorutools.scripts.auto_submit_implications import Series, series_from_config


@pytest.fixture(scope="session")
def series_list() -> list[Series]:
    return series_from_config()


@pytest.mark.implication_bot
@pytest.mark.parametrize("subtag,expected_parent", [
    ("murasaki_shikibu_(swimsuit_rider)_(third_ascension)_(fate)", "murasaki_shikibu_(swimsuit_rider)_(fate)"),
    ("murasaki_shikibu_(swimsuit_rider)_(fate)", "murasaki_shikibu_(fate)"),
    ("tezcatlipoca_(second_ascension)_(fate)", "tezcatlipoca_(fate)"),

    ("male_robin_(festive_tactician)_(fire_emblem)", "male_robin_(fire_emblem)"),

    ("unryuu_kai_(kancolle)", "unryuu_(kancolle)"),
    ("unryuu_kai_ni_(kancolle)", "unryuu_(kancolle)"),

    ("exusiai_the_new_covenant_(costume)_(arknights)", "exusiai_the_new_covenant_(arknights)"),
    ("exusiai_the_new_covenant_(arknights)", "exusiai_(arknights)"),
])
def test_parsing(subtag: str, expected_parent: str, series_list: list[Series]) -> None:
    series_qualifier = re.findall(r"\((.*?)\)", subtag)[-1]
    try:
        series = next(s for s in series_list if s.name == series_qualifier)
    except StopIteration:
        series = Series(name=series_qualifier, topic_id=0, extra_costume_patterns=[])

    assert (parent := series.search_for_main_tag(subtag)) and parent.name == expected_parent
