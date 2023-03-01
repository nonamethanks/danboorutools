import os
from typing import Literal, Sequence, TypeVar

from backoff import expo, on_exception

from danboorutools import logger
from danboorutools.exceptions import DanbooruHTTPError
from danboorutools.logical.sessions import Session
from danboorutools.models.danbooru import (DanbooruArtist, DanbooruCommentVote, DanbooruModel, DanbooruPost, DanbooruPostVersion,
                                           DanbooruPostVote, DanbooruTag, DanbooruUser)
from danboorutools.models.file import File
from danboorutools.models.url import Url
from danboorutools.version import version

GenericModel = TypeVar("GenericModel", bound=DanbooruModel)


class DanbooruApi(Session):
    bad_source_tags = [
        "bad_source",
        "cropped",
        "downscaled",
        "imageboard_desourced",
        "jpeg_artifacts",
        "lossless-lossy",
        "lossy-lossless",
        "md5_mismatch",
        "non-web_source",
        "replaceme",
        "resized",
        "resolution_mismatch",
        "source_larger",
        "source_request",
        "source_smaller",
        "third-party_source",
        "upscaled",
    ]

    only_string_defaults = {
        "artist": "id,created_at,name,other_names,is_deleted,is_banned,tag,urls",
        "comment_vote": "id,created_at,score,is_deleted,user,comment",
        "post_version": "id,updated_at,updater,post,added_tags,removed_tags,obsolete_added_tags,obsolete_removed_tags",
        "post_vote": "id,created_at,score,is_deleted,user,post",
        "tag": "id,name,post_count,category,created_at,is_deprecated,wiki_page,artist",
    }

    def __init__(self, *args,
                 domain: Literal["testbooru", "danbooru"] = "testbooru",
                 mode: Literal["main", "bot"] = "main",
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.base_url = f"https://{domain}.donmai.us"
        if mode == "bot":
            self.auth = (os.environ[f"{domain.upper()}_BOT_USERNAME"], os.environ[f"{domain.upper()}_BOT_API_KEY"])
        else:
            self.auth = (os.environ[f"{domain.upper()}_USERNAME"], os.environ[f"{domain.upper()}_API_KEY"])

    def url_for_search(self, tags: list[str]) -> str:
        tag_string = " ".join(tags)
        return f"{self.base_url}/posts?tags={tag_string}"

    @on_exception(expo, DanbooruHTTPError, max_tries=3)
    def danbooru_request(self, method: str, endpoint: str, *args, **kwargs) -> list[dict] | dict:
        if method == "GET" and "params" in kwargs and endpoint != "posts.json":
            kwargs["params"].setdefault("limit", 1000)

        kwargs["headers"] = {"User-Agent": f"DanbooruTools/{version}"}

        endpoint_url = self.base_url.strip("/") + "/" + endpoint.strip("/")
        response = self.request(method, endpoint_url, *args, **kwargs)

        if not response.ok:
            raise DanbooruHTTPError(response)

        if endpoint.endswith(".json"):
            return self._try_json_response(response)
        else:
            return {
                "success": True
            }

    def posts(self, tags: list[str], page: int | str = 1) -> list[DanbooruPost]:
        if not any(t.startswith("limit:") for t in tags):
            tags += ["limit:200"]

        params = {
            "tags": " ".join(tags),
            "page": page
        }

        response = self.danbooru_request("GET", "posts.json", params=params)
        posts = [DanbooruPost(post_data) for post_data in response]
        return posts

    def all_posts(self, tags: list[str]) -> list[DanbooruPost]:
        posts: list[DanbooruPost] = []
        page: int | str = 1
        while True:
            logger.info(f"Collecting posts for the search {tags}: at page {page}, found: {len(posts)}")
            found_posts = self.posts(tags, page=page)
            if not found_posts:
                logger.info(f"Done. Found {len(posts)} posts.")
                return posts
            posts += found_posts
            lowest_id = min(found_posts, key=lambda post: post.id).id
            page = f"b{lowest_id}"

    def users(self, **kwargs) -> list[DanbooruUser]:
        params = kwargs_to_include(**kwargs)
        response = self.danbooru_request("GET", "users.json", params=params)
        users = [DanbooruUser(user_data) for user_data in response]
        return users

    def _generic_endpoint(self, model_type: type[GenericModel], **kwargs) -> list[GenericModel]:
        only_string = self.only_string_defaults.get(model_type.model_name)
        params = kwargs_to_include(**kwargs, only=only_string)
        response = self.danbooru_request("GET", f"{model_type.model_name}s.json", params=params)
        models = [model_type(model_data) for model_data in response]
        return models

    def artists(self, **kwargs) -> list[DanbooruArtist]:
        return self._generic_endpoint(DanbooruArtist, **kwargs)

    def comment_votes(self, **kwargs) -> list[DanbooruCommentVote]:
        return self._generic_endpoint(DanbooruCommentVote, **kwargs)

    def post_versions(self, **kwargs) -> list[DanbooruPostVersion]:
        return self._generic_endpoint(DanbooruPostVersion, **kwargs)

    def post_votes(self, **kwargs) -> list[DanbooruPostVote]:
        return self._generic_endpoint(DanbooruPostVote, **kwargs)

    def tags(self, **kwargs) -> list[DanbooruTag]:
        return self._generic_endpoint(DanbooruTag, **kwargs)

    def create_artist(self, name: str, other_names: list[str], urls: Sequence[Url | str]) -> None:
        final_urls = [Url.parse(url) for url in urls]
        url_string = [f"-{u.normalized_url}" if u.is_deleted else u.normalized_url for u in final_urls]
        logger.info(f"Creating artist {name} with urls '{url_string}'")

        data = {
            "artist": {
                "name": name,
                "url_string": " ".join(url_string),
                "other_names_string": " ".join(other_names)
            }
        }
        request = self.danbooru_request("POST", "artists", json=data)
        assert isinstance(request, dict) and request["success"] is True

    def update_post_tags(self, post: DanbooruPost, tags: list[str]) -> None:
        """Update a post's tags."""
        tag_string = " ".join(tags)
        logger.info(f"Sending tags {tag_string} to post {post.url}")
        data = {
            "post": {
                "tag_string": tag_string,
                "old_tag_string": ""
            }
        }
        response = self.danbooru_request("PUT", f"posts/{post.id}", json=data)
        assert isinstance(response, dict) and response["success"] is True

    def update_artist_urls(self, artist: DanbooruArtist, urls: Sequence[Url | str]) -> None:
        parsed_urls = [Url.parse(url) for url in urls]
        url_string = [f"-{u.normalized_url}" if u.is_deleted else u.normalized_url for u in parsed_urls + artist.urls]
        logger.info(f"Sending urls '{url_string}' to artist {artist}")

        data = {
            "artist": {
                "url_string": " ".join(url_string),
            }
        }
        request = self.danbooru_request("PUT", artist.model_path, json=data)
        assert isinstance(request, dict) and request["success"] is True

    def replace(self,
                post: DanbooruPost,
                replacement_file: File | None = None,
                replacement_url: Url | str | None = None,
                final_source: Url | str | None = None
                ) -> None:
        if not replacement_file and not replacement_url:
            raise ValueError("Either a file or an url must be present.")

        if replacement_file and replacement_url:
            raise ValueError("Only one of file and url must be present.")

        if replacement_url:
            raise NotImplementedError
        assert replacement_file
        if replacement_file.md5 == post.md5:
            logger.info(f"Skipping replacement for {post} with {replacement_url or replacement_file}: same file.")
            return

        final_source = final_source if final_source else post.source
        if isinstance(final_source, Url):
            final_source = final_source.normalized_url

        tags_to_send = [f"-{t}" for t in self.bad_source_tags]
        tags_to_send += [f"-{t}" for t in post.meta_tags if t.endswith("_sample")]

        data = {
            "post_replacement[replacement_url]": (None, ""),
            "post_replacement[final_source]": (None, final_source),
            "post_replacement[tags]": (None, " ".join(tags_to_send)),
            "post_replacement[replacement_file]": (str(replacement_file.path), replacement_file.path.open("rb")),
        }

        self.danbooru_request("POST", f"post_replacements?post_id={post.id}", files=data)
        logger.info(f"Replaced {post} with {replacement_url or replacement_file}")


def kwargs_to_include(**kwargs) -> dict:
    """Turn kwargs into url parameters that Rails can understand."""
    params = {}
    for named_parameter in ["only", "page", "limit"]:
        if n_p := kwargs.pop(named_parameter, None):
            params[named_parameter] = n_p

    for _key, _value in kwargs.items():
        parsed_key = f"search[{_key}]"
        for extra_key, parsed_value in _parse_to_include(_value):
            params[parsed_key + extra_key] = parsed_value
    return params


def _parse_to_include(obj: str | dict) -> list[tuple[str, str]]:
    if isinstance(obj, dict):
        keys_and_values: list[tuple[str, str]] = []
        for [_key, _val] in obj.items():
            parsed_key = f"[{_key}]"
            for extra_key, parsed_value in _parse_to_include(_val):
                keys_and_values.append((parsed_key + extra_key, parsed_value))
        return keys_and_values
    else:
        return [("", obj)]


danbooru_api = DanbooruApi(domain="danbooru", mode="bot")
