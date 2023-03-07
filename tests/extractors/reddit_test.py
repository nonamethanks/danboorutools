from danboorutools.logical.extractors.reddit import RedditPostUrl, RedditUserUrl
from tests.extractors import assert_info_url, generate_parsing_suite

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
    }
}


generate_parsing_suite(urls)

assert_info_url(
    "https://www.reddit.com/user/imsleepyzen",
    url_properties=dict(username="imsleepyzen"),
    url_type=RedditUserUrl,
    related=["https://twitter.com/imsleepyzen", "https://www.instagram.com/imsleepyzen"],
    primary_names=["imsleepyzen"],
    secondary_names=[],
)
