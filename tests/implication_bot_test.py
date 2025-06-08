import pytest

from danboorutools.scripts.auto_submit_implications import DanbooruTagData, Series, series_from_config


@pytest.fixture(scope="session")
def series_list() -> list[Series]:
    series = series_from_config()
    return series


TEST_CASES = {
    "fate": [
        ("miyamoto_musashi_(swimsuit_berserker)_(second_ascension)_(fate)", "miyamoto_musashi_(swimsuit_berserker)_(fate)"),
        ("murasaki_shikibu_(swimsuit_rider)_(third_ascension)_(fate)", "murasaki_shikibu_(fate)"),
        ("murasaki_shikibu_(swimsuit_rider)_(fate)", "murasaki_shikibu_(fate)"),
        ("tezcatlipoca_(second_ascension)_(fate)", "tezcatlipoca_(fate)"),
    ],
    "fire_emblem": [
        ("male_robin_(festive_tactician)_(fire_emblem)", "male_robin_(fire_emblem)"),
    ],
    "kancolle": [
        ("unryuu_kai_(kancolle)", "unryuu_(kancolle)"),
        ("unryuu_kai_ni_(kancolle)", "unryuu_(kancolle)"),
    ],
    "arknights": [
        ("exusiai_the_new_covenant_(costume)_(arknights)", "exusiai_the_new_covenant_(arknights)"),
        ("exusiai_the_new_covenant_(arknights)", "exusiai_(arknights)"),
    ],
    "identity_v": [
        ("florian_brand_(spirit_fox)", "florian_brand"),
    ],
    "pgr": [
        ("sophia:_silverfang_(starry_desert)_(pgr)", "sophia_(pgr)"),
    ],
}
TEST_CASES_PARSED = [[series, subtag, expected_parent] for series in TEST_CASES for (subtag, expected_parent) in TEST_CASES[series]]


@pytest.mark.implication_bot
@pytest.mark.parametrize("series_name,subtag,expected_parent", TEST_CASES_PARSED)
def test_parsing(series_name: str, subtag: str, expected_parent: str, series_list: list[Series]) -> None:
    try:
        series = next(s for s in series_list if s.matches(series_name))
    except StopIteration:
        series = Series(name=series_name, topic_id=0, extra_costume_patterns=[])

    tag = DanbooruTagData(
        id=0,
        name=subtag,
        antecedent_implications=[],
        wiki_page=None,
        is_deprecated=False,
        post_count=100,
    )

    parent = series.get_parent_for_tag(tag)
    assert parent
    assert parent.name == expected_parent
