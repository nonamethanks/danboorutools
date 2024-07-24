from collections.abc import Iterator, Sequence

from danboorutools.logical.sessions.misskey import MisskeyPostData, MisskeySession, MisskeyUserData
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, RedirectUrl, Url, parse_list


class MisskeyUrl(Url):
    session = MisskeySession()


class MisskeyUserUrl(ArtistUrl, MisskeyUrl):
    username: str

    normalize_template = "https://misskey.io/@{username}"

    @property
    def artist_data(self) -> MisskeyUserData:
        return self.session.artist_data(self.username)

    @property
    def primary_names(self) -> list[str]:
        if self.artist_data.name:
            return [self.artist_data.name]
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls

    def _extract_posts_from_each_page(self) -> Iterator[list[MisskeyPostData]]:
        until_id = None
        while True:
            yield (posts := self.session.posts(user_id=self.artist_data.id, until_id=until_id))
            until_id = posts[-1].id

    def _process_post(self, post_object: MisskeyPostData) -> None:
        post = MisskeyNoteUrl.build(note_id=post_object.id)
        post.gallery = self

        self._register_post(
            post=post,
            assets=[f.url for f in post_object.files],
            created_at=post_object.createdAt,
            score=post_object.reactionCount,
        )

    def _extract_assets(self) -> list[GalleryAssetUrl]:
        return []


class MisskeyUserIdUrl(RedirectUrl, MisskeyUrl):
    user_id: str

    normalize_template = "https://misskey.io/users/{user_id}"


class MisskeyNoteUrl(PostUrl, MisskeyUrl):
    note_id: str
    normalize_template = "https://misskey.io/notes/{note_id}"


class MisskeyAssetUrl(PostAssetUrl, MisskeyUrl):

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query
