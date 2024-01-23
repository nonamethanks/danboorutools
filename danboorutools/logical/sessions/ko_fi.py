from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from danboorutools.logical.sessions import Session

if TYPE_CHECKING:
    from danboorutools.logical.urls.ko_fi import KoFiArtistUrl, KoFiPostUrl

onclick_pattern = re.compile(r"^viewImageFromFeed\('[\w-]+', '(?P<post_id>\w+)'\)$")


class KoFiSession(Session):
    @property
    def cookies_from_env(self) -> dict:
        return {".AspNet.ApplicationCookie": os.environ["KOFI_ASPNET_APPLICATION_COOKIE"]}

    @property
    def followed_artists(self) -> list[KoFiArtistUrl]:
        html = self.get("https://ko-fi.com/manage/following", cookies=self.cookies_from_env).html
        artists = [el.attrs["href"] for el in html.select(".person-row-name-link")]
        return artists

    def get_feed(self, page: int = 0) -> list[KoFiPostUrl]:
        followed = self.followed_artists

        from danboorutools.logical.urls.ko_fi import KoFiArtistUrl, KoFiPostUrl

        html = self.get(f"https://ko-fi.com/Feed/LoadNewsfeedPage?pageIndex={page}", cookies=self.cookies_from_env).html
        collected: list[KoFiPostUrl] = []
        feed_items = html.select(".feeditem-unit:has(.feeditem-imagecontainer):not(:has(.kfds-c-locked-overlay-wrapper))")
        if not feed_items:
            raise NotImplementedError("No posts found. Check cookie.")
        for feed_item in feed_items:
            artist_str = urljoin("https://ko-fi.com/", feed_item.select_one(".feeditem-thumbcontainer a").attrs["href"])
            artist = KoFiPostUrl.parse(artist_str)
            assert isinstance(artist, KoFiArtistUrl), (artist, artist_str)

            if artist not in followed:
                continue

            onclick = feed_item.select_one(".kfds-c-srf-image-update-feedwrapper  img")["onclick"]
            if not (match := onclick_pattern.match(onclick)):
                raise NotImplementedError(onclick)
            post = KoFiPostUrl.build(post_id=match.groupdict()["post_id"])
            score = feed_item.select("span[class^='like-count-']")[1].text.strip() or 0
            post.score = int(score)
            collected += [post]

        return collected
