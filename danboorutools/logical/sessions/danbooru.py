import os
from typing import Literal

from danboorutools import logger
from danboorutools.exceptions import DanbooruHTTPError
from danboorutools.logical.sessions import Session
from danboorutools.models.base_url import BaseUrl
from danboorutools.models.danbooru import DanbooruCommentVote, DanbooruPost, DanbooruPostVote, DanbooruUser
from danboorutools.models.file import File
from danboorutools.version import version


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

    def danbooru_request(self, method: str, endpoint: str, *args, **kwargs) -> list[dict] | dict:
        if method == "GET" and "params" in kwargs:
            limit = 200 if endpoint == "posts" else 1000
            kwargs["params"].setdefault("limit", limit)

        kwargs["headers"] = {"User-Agent": f"DanbooruTools/{version}"}

        endpoint_url = self.base_url.strip("/") + "/" + endpoint.strip("/")

        response = self.request(method, endpoint_url, *args, **kwargs)

        if not response.ok:
            raise DanbooruHTTPError(response)

        if endpoint.endswith(".json"):
            return response.json()
        else:
            return {
                "success": True
            }

    def posts(self, tags: list[str], page: int | str = 1) -> list[DanbooruPost]:
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
            logger.info(f"Collecting posts: at page {page}, found: {len(posts)}")
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

    def post_votes(self, **kwargs) -> list[DanbooruPostVote]:
        only = "id,created_at,score,is_deleted,user,post"
        params = kwargs_to_include(**kwargs, only=only)
        response = self.danbooru_request("GET", "post_votes.json", params=params)
        post_votes = [DanbooruPostVote(post_vote_data) for post_vote_data in response]
        return post_votes

    def comment_votes(self, **kwargs) -> list[DanbooruCommentVote]:
        only = "id,created_at,score,is_deleted,user,comment"
        params = kwargs_to_include(**kwargs, only=only)
        response = self.danbooru_request("GET", "comment_votes.json", params=params)
        comment_votes = [DanbooruCommentVote(comment_vote_data) for comment_vote_data in response]
        return comment_votes

    def replace(self,
                post: DanbooruPost,
                replacement_file: File | None = None,
                replacement_url: BaseUrl | None = None,
                final_source: BaseUrl | None = None
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

        tags_to_send = [f"-{t}" for t in self.bad_source_tags]
        tags_to_send += [f"-{t}" for t in post.meta_tags if t.endswith("_sample")]

        data = {
            "post_replacement[replacement_url]": (None, ""),
            "post_replacement[final_source]": (None, final_source.normalized_url),
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
