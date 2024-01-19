import pytest

from danboorutools.logical.urls.reddit import RedditPostRedirectUrl, RedditPostUrl, RedditUserUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestInfoUrl, _TestRedirectUrl

urls = {
    RedditUserUrl: {
        "http://www.reddit.com/user/TouchFluffyTailss/": "https://www.reddit.com/user/TouchFluffyTailss",
        "https://old.reddit.com/user/Ok-Aerie-1683/submitted/": "https://www.reddit.com/user/Ok-Aerie-1683",
    },
    RedditPostUrl: {
        "https://www.reddit.com/r/Overwatch/comments/4zjb8t/kunoichi_widowmaker_concept_art/": "https://www.reddit.com/r/Overwatch/comments/4zjb8t/kunoichi_widowmaker_concept_art",
        "https://www.reddit.com/r/Overwatch/comments/4zjb8t": "https://www.reddit.com/r/Overwatch/comments/4zjb8t",
        "https://www.reddit.com/user/blank_page_drawings/comments/nfjz0d/a_sleepy_orc/": "https://www.reddit.com/user/blank_page_drawings/comments/nfjz0d/a_sleepy_orc",
        "https://www.reddit.com/user/blank_page_drawings/comments/nfjz0d/": "https://www.reddit.com/user/blank_page_drawings/comments/nfjz0d",

        "https://www.reddit.com/comments/ttyccp": "https://www.reddit.com/comments/ttyccp",
        "https://www.reddit.com/gallery/ttyccp": "https://www.reddit.com/comments/ttyccp",
        "https://www.reddit.com/ttyccp": "https://www.reddit.com/comments/ttyccp",
        "http://www.reddit.com/r/Kappa/comments/34d761/shirt_idea_for_alex_myers_sponsorship/cqu5yc3": "https://www.reddit.com/r/Kappa/comments/34d761/shirt_idea_for_alex_myers_sponsorship/cqu5yc3",
    },
    RedditPostRedirectUrl: {
        "https://www.reddit.com/r/Afrobull/s/EvhJrKokJV": "https://www.reddit.com/r/Afrobull/s/EvhJrKokJV",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestRedditUserUrl1(_TestInfoUrl):
    url_string = "https://www.reddit.com/user/imsleepyzen"
    url_properties = dict(username="imsleepyzen")
    url_type = RedditUserUrl
    related = ["https://twitter.com/imsleepyzen", "https://www.instagram.com/imsleepyzen"]
    primary_names = ["imsleepyzen"]
    secondary_names = []


class TestRedditUserUrl2(_TestInfoUrl):
    url_string = "https://www.reddit.com/user/AkioAsaku"
    url_type = RedditUserUrl
    url_properties = dict(username="AkioAsaku")
    primary_names = ["AkioAsaku"]
    secondary_names = []
    related = []
    is_deleted = True


class TestRedditRedirectPostUrl(_TestRedirectUrl):
    url_string = "https://www.reddit.com/r/Afrobull/s/EvhJrKokJV"
    url_type = RedditPostRedirectUrl
    url_properties = dict(redirect_post_id="EvhJrKokJV", subreddit="Afrobull")
    redirects_to = "https://www.reddit.com/r/Afrobull/comments/186gyjb/november_2023_fanart_poll_winner_%F0%9D%97%96%F0%9D%97%AE%F0%9D%97%BA%F0%9D%97%BA%F0%9D%98%86_street"
