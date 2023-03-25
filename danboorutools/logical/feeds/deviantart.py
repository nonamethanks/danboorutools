from danboorutools.logical.sessions.deviantart import DeviantartSession
from danboorutools.logical.urls.deviantart import DeviantArtImageUrl, DeviantArtPostUrl
from danboorutools.models.feed import FeedWithSeparateArtists


class DeviantartFeed(FeedWithSeparateArtists):
    session = DeviantartSession()

    _extract_artists = session.get_followed_artists

    def _extract_posts_from_each_artist(self, artist: str) -> None:
        offset = 0
        page = 1
        while True:
            if page > self.quit_early_page:
                return

            get_data = {
                "username": artist,
                "offset": offset,
                "limit": 24,
                "mature_content": True,
            }
            page_json = self.session.api._req("/gallery/all", get_data=get_data)

            for post_data in page_json["results"]:
                self._process_json_post(post_data)

            if not page_json["has_more"]:
                return

            offset = page_json["next_offset"]

            page += 1

    def _process_json_post(self, post_object: dict) -> None:
        post = DeviantArtPostUrl.parse(post_object["url"])
        assert isinstance(post, DeviantArtPostUrl)

        created_at = int(post_object["published_time"])
        score = post_object["stats"]["favourites"]

        post.uuid = post_object["deviationid"]

        if post_object["is_downloadable"]:
            resp = self.session.api._req(f"/deviation/download/{post.uuid}", get_data={"mature_content": True})
            image_str = resp["src"]
        else:
            if "content" not in post_object:
                return
            image_sample = post_object["content"]["src"]
            image_str = DeviantArtImageUrl._extract_best_image(image_sample)

        image = DeviantArtImageUrl.parse(image_str)
        assert isinstance(image, DeviantArtImageUrl)

        self._register_post(
            post=post,
            assets=[image],
            created_at=created_at,
            score=score,
        )
