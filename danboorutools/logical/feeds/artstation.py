from danboorutools.logical.sessions.artstation import ArtstationSession
from danboorutools.logical.urls.artstation import ArtStationPostUrl
from danboorutools.models.feed import JsonFeedWithSeparateArtists
from danboorutools.models.url import PostAssetUrl, Url


class ArtstationFeed(JsonFeedWithSeparateArtists):
    session = ArtstationSession()

    _extract_artists = session.get_followed_artists

    posts_json_url = "https://www.artstation.com/users/{artist}/projects.json?page={{page}}"
    posts_objects_dig = ["data"]

    def _process_json_post(self, post_object: dict) -> None:
        if post_object["icons"]["pano"]:
            return

        post = Url.parse(post_object["permalink"])
        assert isinstance(post, ArtStationPostUrl)

        created_at = post_object["created_at"]
        score = post_object["likes_count"]

        if post_object["assets_count"] == 1:
            asset = Url.parse(post_object["cover"]["small_square_url"])
            assert isinstance(asset, PostAssetUrl)
            assets = [asset]

        else:
            assets = post.assets

        self._register_post(
            post=post,
            assets=assets,
            created_at=created_at,
            score=score,
        )
