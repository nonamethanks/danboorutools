from collections.abc import Iterator
from itertools import count, repeat

from danboorutools.logical.sessions.artstation import ArtstationPostData, ArtstationSession
from danboorutools.logical.urls.artstation import ArtStationPostUrl
from danboorutools.models.feed import FeedWithSeparateArtists
from danboorutools.models.url import PostAssetUrl, Url


class ArtstationFeed(FeedWithSeparateArtists):
    session = ArtstationSession()

    _extract_artists = session.get_followed_artists

    def _extract_posts_from_each_artist(self, artist: str) -> Iterator[list[ArtstationPostData]]:
        return map(self.session.get_posts_from_artist, zip(repeat(artist), count(1), strict=True))

    def _process_post(self, post_object: ArtstationPostData) -> None:
        if post_object.icons["pano"]:
            return

        post = Url.parse(post_object.permalink)
        assert isinstance(post, ArtStationPostUrl)

        if post_object.asset_count == 1:
            asset = Url.parse(post_object.cover["small_square_url"])
            assert isinstance(asset, PostAssetUrl)
            assets = [asset]

        else:
            assets = post.assets

        self._register_post(
            post=post,
            assets=assets,
            created_at=post_object.created_at,
            score=post_object.likes_count,
        )
