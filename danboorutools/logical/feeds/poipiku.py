import time
from collections.abc import Iterator

from danboorutools import logger
from danboorutools.logical.sessions.poipiku import PoipikuSession
from danboorutools.logical.urls.poipiku import DUMMY_IMGS, PoipikuImageUrl, PoipikuPostUrl
from danboorutools.models.feed import Feed
from danboorutools.models.url import parse_list


class PoipikuFeed(Feed):
    session = PoipikuSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[tuple[PoipikuPostUrl, list[PoipikuImageUrl]]]]:
        page = 0
        self.session.init_browser()
        while True:
            page_url = f"https://poipiku.com/MyHomePcV.jsp?PG={page}"

            browser = self.session.browser
            browser.get(page_url)

            post_urls_and_imgs: list[PoipikuPostUrl] = []
            for post_element in browser.find_elements("css selector", ".IllustItem"):
                if post_element.find_elements("css selector", ".IllustItemExpandPass"):
                    logger.warning("Could not extract assets from a post because of password protection.")
                    continue
                if (expand := post_element.find_elements("css selector", ".IllustItemExpandBtn")):
                    browser.execute_script("arguments[0].click()", expand[0])
                    browser.wait_for_request("ShowAppendFileF")
                    time.sleep(1)

                assets_urls = [
                    i_e.get_attribute("src") for i_e in
                    post_element.find_elements("css selector", ".IllustItemThumbImg")
                ]

                assets_urls = [
                    img for img in assets_urls
                    if img not in DUMMY_IMGS
                ]

                assets = parse_list(assets_urls, PoipikuImageUrl)
                assert assets

                post_urls_and_imgs.append((assets[0].post, assets))

            yield post_urls_and_imgs

            page += 1

    def _process_post(self, post_object: tuple[PoipikuPostUrl, list[PoipikuImageUrl]]) -> None:
        post, assets = post_object
        self._register_post(
            post,
            assets=assets,
            created_at=assets[0].created_at,
            score=post.score,
        )

    @property
    def normalized_url(self) -> str:
        return "https://poipiku.com/MyHomePcV.jsp"
