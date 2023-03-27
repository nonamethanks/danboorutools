from collections.abc import Iterator

from danboorutools.logical.sessions.deviantart import DeviantartPostData, DeviantartSession
from danboorutools.logical.urls.deviantart import DeviantArtImageUrl, DeviantArtPostUrl
from danboorutools.models.feed import FeedWithSeparateArtists


class DeviantartFeed(FeedWithSeparateArtists):
    session = DeviantartSession()

    _extract_artists = session.get_followed_artists

    def _extract_posts_from_each_artist(self, artist: str) -> Iterator[list[DeviantartPostData]]:
        offset = 0
        while True:
            data = self.session.get_artist_posts(artist, offset=offset)

            if not data.has_more:
                return

            assert data.next_offset
            offset = data.next_offset

            yield data.results

    def _process_post(self, post_object: DeviantartPostData) -> None:
        post = DeviantArtPostUrl.parse(post_object.url)
        assert isinstance(post, DeviantArtPostUrl)

        post.uuid = post_object.deviationid

        if post_object.is_downloadable:
            image_str = self.session.get_download_url(post.uuid)
        else:
            image_sample = post_object.content["src"]
            image_str = DeviantArtImageUrl._extract_best_image(image_sample)

        image = DeviantArtImageUrl.parse(image_str)
        assert isinstance(image, DeviantArtImageUrl)

        self._register_post(
            post=post,
            assets=[image],
            created_at=post_object.published_time,
            score=post_object.stats["favourites"],
        )
