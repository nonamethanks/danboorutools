from collections.abc import Iterator

from danboorutools.logical.sessions.nicovideo import NicoSeigaPostData, NicovideoSession
from danboorutools.logical.urls.nicoseiga import NicoSeigaArtistUrl, NicoSeigaIllustUrl
from danboorutools.models.feed import Feed
from danboorutools.models.url import Url


class NicoSeigaFeed(Feed):
    session = NicovideoSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[NicoSeigaPostData]]:

        min_id = 0
        seen_ids: list[str] = []
        while True:
            page_data = self.session.get_nicoseiga_feed(min_id=min_id or None)

            if not min_id and not page_data.data:
                raise NotImplementedError("No posts found. Check cookies.")

            yield [p for p in page_data.data if p.object["url"] not in seen_ids]
            # why tf does nicovideo return dupes like this
            seen_ids += [p.object["url"] for p in page_data.data]

            if not page_data.meta["hasNext"]:
                return

            min_id = page_data.meta["minId"]

    def _process_post(self, post_object: NicoSeigaPostData) -> None:
        if post_object.object["type"] != "image":
            return

        post = Url.parse(post_object.object["url"])
        assert isinstance(post, NicoSeigaIllustUrl)
        post.gallery = Url.build(NicoSeigaArtistUrl, user_id=int(post_object.muteContext["sender"]["id"]))

        image = f"https://seiga.nicovideo.jp/image/source/{post.illust_id}"

        self._register_post(
            post=post,
            assets=[image],
            score=0,
            created_at=post_object.updated,
        )
