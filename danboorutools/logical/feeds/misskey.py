from collections.abc import Iterator

from danboorutools.logical.sessions.misskey import MisskeyPostData, MisskeySession
from danboorutools.logical.urls.misskey import MisskeyNoteUrl, MisskeyUserUrl
from danboorutools.models.feed import Feed


class MisskeyFeed(Feed):
    session = MisskeySession()
    domain: str

    def _extract_posts_from_each_page(self) -> Iterator[list[MisskeyPostData]]:
        until_id = None
        while True:
            yield (posts := self.session.feed(until_id=until_id))
            until_id = posts[-1].id

    def _process_post(self, post_object: MisskeyPostData) -> None:
        post = MisskeyNoteUrl.build(note_id=post_object.id)
        post.gallery = MisskeyUserUrl.build(username=post_object.user.username)

        self._register_post(
            post=post,
            assets=[f.url for f in post_object.files],
            created_at=post_object.createdAt,
            score=post_object.reactionCount,
        )

    @property
    def normalized_url(self) -> str:
        return "https://misskey.art/"
