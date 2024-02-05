from collections.abc import Iterator

from danboorutools import logger
from danboorutools.models.url import ArtistUrl, PostUrl, Url


class SubscribestarUrl(Url):
    ...


class SubscribestarArtistUrl(ArtistUrl, SubscribestarUrl):
    username: str

    normalize_template = "https://subscribestar.adult/{username}"

    @property
    def primary_names(self) -> list[str]:
        return [self.username]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []

    def _extract_posts_from_each_page(self) -> Iterator[list]:
        if "profile is under review" in self.html:
            logger.info("Profile is under review. No posts to scrape.")
            return
        raise NotImplementedError


class SubscribestarPostUrl(PostUrl, SubscribestarUrl):
    post_id: int

    normalize_template = "https://subscribestar.adult/posts/{post_id}"
