from __future__ import annotations

import os
import random
import time
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Literal, TypeVar, overload

from backoff import expo, on_exception
from cloudscraper.exceptions import CloudflareChallengeError
from pydantic import BaseModel
from requests import JSONDecodeError
from requests.exceptions import ReadTimeout

from danboorutools import logger
from danboorutools.exceptions import DanbooruHTTPError, RateLimitError, ShieldedUrlError
from danboorutools.logical.progress_tracker import ProgressTracker
from danboorutools.logical.sessions import Session
from danboorutools.models import danbooru as models
from danboorutools.models.url import UnknownUrl, Url, UselessUrl

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from danboorutools.models.file import File

GenericDanbooruModel = TypeVar("GenericDanbooruModel", bound=models.DanbooruModel)
GenericModel = TypeVar("GenericModel", bound=BaseModel)


class DanbooruApi(Session):
    DEFAULT_USER_AGENT = "DanbooruTools/0.1.0"
    DISABLE_AUTOMATIC_CACHE = True
    DEFAULT_TIMEOUT = 60

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
        "ban": "id,created_at,duration,reason,user,banner",
        "comment_vote": "id,created_at,score,is_deleted,user,comment",
        "comment": "id,created_at,is_deleted,post,creator,body,score",
        "forum_post": "id,created_at,updated_at,is_deleted,creator,topic,body",
        "media_asset": "id,created_at,md5,file_ext,file_size,image_width,image_height,duration,pixel_hash,variants,post",
        "post_appeal": "id,created_at,post,creator,reason,status",
        "post_flag": "id,created_at,reason,post,is_resolved,status,category",
        "post_version": "id,updated_at,updater,post,added_tags,removed_tags,obsolete_added_tags,obsolete_removed_tags",
        "post_replacement": "id,created_at,post",
        "post_vote": "id,created_at,score,is_deleted,user,post",
        "tag": "id,name,post_count,category,created_at,is_deprecated,wiki_page,artist,antecedent_implications,consequent_implications",
        "tag_implication": "id,reason,creator,approver,antecedent_tag,consequent_tag,created_at,updated_at",
        "user": "id,name,created_at,level,level_string,post_update_count,note_update_count,post_upload_count,is_banned,is_deleted,bans,last_ip_addr",  # noqa: E501
        "user_feedback": "id,category,body,user,creator,created_at,updated_at,is_deleted",
        "wiki_page": "id,created_at,updated_at,title,body,is_locked,other_names"
    }
    only_string_defaults["user_event"] = f"id,created_at,category,user_session,user[{only_string_defaults["user"]}]"

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

    @on_exception(expo, (DanbooruHTTPError, ReadTimeout), max_tries=5)
    def danbooru_request(self, method: str, endpoint: str, *args, **kwargs) -> list[dict] | dict:
        if method == "GET" and "params" in kwargs and endpoint not in ["posts.json", "counts/posts.json"]:
            kwargs["params"].setdefault("limit", 1000)
        elif endpoint == "posts.json":
            kwargs["params"].setdefault("limit", 200)

        endpoint_url = self.base_url.strip("/") + "/" + endpoint.strip("/")
        response = self.request(method, endpoint_url, *args, **kwargs)

        if not response.ok:
            raise DanbooruHTTPError(response)

        try:
            return response.json()
        except JSONDecodeError:
            return {"success": True}

    def posts(self, tags: list[str], page: int | str = 1) -> list[models.DanbooruPost]:
        params = {
            "tags": " ".join(tags),
            "page": page,
        }

        response = self.danbooru_request("GET", "posts.json", params=params)
        return [models.DanbooruPost(**post_data) for post_data in response]

    def post_counts(self, tags: list[str], hard_refresh: bool = False, use_cache: bool = True) -> int:
        if hard_refresh:
            tags = [t for t in tags if not t.startswith("order:")] + [f"order:{random.randint(1, int(1e10))}"]
        elif use_cache and (cached := self._get_cached_counts(tags)) is not None:
            logger.trace(f"Returning cached value for search {tags}: {cached}")
            return cached

        params = {
            "tags": " ".join(tags),
        }

        response = self.danbooru_request("GET", "counts/posts.json", params=params)
        count = response["counts"]["posts"]  # type: ignore[call-overload]
        self._save_count(tags, count)
        return count

    def _get_cached_counts(self, tags: list[str]) -> int | None:
        tag_str = " ".join(sorted(t.strip() for t in tags))
        val = ProgressTracker(f"DANBOORU_TAG_COUNTS_{tag_str}", ",").value
        last_checked, count = val.split(",")
        if self._was_saved_recently(last_checked):
            return int(count)
        return None

    def _save_count(self, tags: list[str], count: int) -> None:
        tag_str = " ".join(sorted(t.strip() for t in tags))
        ProgressTracker(f"DANBOORU_TAG_COUNTS_{tag_str}", "").value = f"{time.time()},{count}"

    def _was_saved_recently(self, timestamp: str, max_hours: int = 1) -> bool:
        if not timestamp:
            return False

        return datetime.fromtimestamp(float(timestamp), tz=UTC) > datetime.now(tz=UTC) - timedelta(hours=max_hours)

    def get_last_edit_time(self, user_name: str) -> datetime | None:
        val = ProgressTracker(f"DANBOORU_USER_LAST_EDIT_{user_name}", ",")
        last_checked, last_edit = val.value.split(",")
        if self._was_saved_recently(last_checked, max_hours=23):
            return datetime.fromtimestamp(float(last_edit), tz=UTC) if last_edit else None

        versions = self.post_versions(updater_name=user_name, limit=1)
        last_version_time = versions[0].updated_at if versions else None
        val.value = f"{time.time()},{last_version_time.timestamp() if last_version_time else ""}"
        return last_version_time

    def all_posts(self, tags: list[str]) -> list[models.DanbooruPost]:
        posts: list[models.DanbooruPost] = []
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

    def _generic_endpoint(self, model_type: type[GenericDanbooruModel], **kwargs) -> list[GenericDanbooruModel]:
        assert model_type.danbooru_model_name
        only_string = self.only_string_defaults.get(model_type.danbooru_model_name)
        params = kwargs_to_include(**kwargs, only=only_string)
        response = self.danbooru_request("GET", f"{model_type.danbooru_model_name}s.json", params=params)
        return [model_type(**model_data) for model_data in response]

    def artists(self, **kwargs) -> list[models.DanbooruArtist]:
        return self._generic_endpoint(models.DanbooruArtist, **kwargs)

    def post_replacements(self, **kwargs) -> list[models.DanbooruReplacement]:
        return self._generic_endpoint(models.DanbooruReplacement, **kwargs)

    def bans(self, **kwargs) -> list[models.DanbooruBan]:
        return self._generic_endpoint(models.DanbooruBan, **kwargs)

    def bulk_update_requests(self, **kwargs) -> list[models.DanbooruBulkUpdateRequest]:
        return self._generic_endpoint(models.DanbooruBulkUpdateRequest, **kwargs)

    def comments(self, **kwargs) -> list[models.DanbooruComment]:
        return self._generic_endpoint(models.DanbooruComment, **kwargs)

    def comment_votes(self, **kwargs) -> list[models.DanbooruCommentVote]:
        return self._generic_endpoint(models.DanbooruCommentVote, **kwargs)

    def dmails(self, **kwargs) -> list[models.DanbooruDmail]:
        return self._generic_endpoint(models.DanbooruDmail, **kwargs)

    def feedbacks(self, **kwargs) -> list[models.DanbooruFeedback]:
        return self._generic_endpoint(models.DanbooruFeedback, **kwargs)

    def media_assets(self, **kwargs) -> list[models.DanbooruMediaAsset]:
        return self._generic_endpoint(models.DanbooruMediaAsset, **kwargs)

    def forum_posts(self, **kwargs) -> list[models.DanbooruForumPost]:
        return self._generic_endpoint(models.DanbooruForumPost, **kwargs)

    def flags(self, **kwargs) -> list[models.DanbooruFlag]:
        return self._generic_endpoint(models.DanbooruFlag, **kwargs)

    def appeals(self, **kwargs) -> list[models.DanbooruAppeal]:
        return self._generic_endpoint(models.DanbooruAppeal, **kwargs)

    def post_versions(self, **kwargs) -> list[models.DanbooruPostVersion]:
        return self._generic_endpoint(models.DanbooruPostVersion, **kwargs)

    def post_votes(self, **kwargs) -> list[models.DanbooruPostVote]:
        return self._generic_endpoint(models.DanbooruPostVote, **kwargs)

    def tags(self, **kwargs) -> list[models.DanbooruTag]:
        return self._generic_endpoint(models.DanbooruTag, **kwargs)

    def tag_implications(self, **kwargs) -> list[models.DanbooruTagImplication]:
        return self._generic_endpoint(models.DanbooruTagImplication, **kwargs)

    def users(self, **kwargs) -> list[models.DanbooruUser]:
        return self._generic_endpoint(models.DanbooruUser, **kwargs)

    def user_events(self, **kwargs) -> list[models.DanbooruUserEvent]:
        return self._generic_endpoint(models.DanbooruUserEvent, **kwargs)

    def wiki_pages(self, **kwargs) -> list[models.DanbooruWikiPage]:
        return self._generic_endpoint(models.DanbooruWikiPage, **kwargs)

    @overload
    def get_all(self, model: type[GenericDanbooruModel], to_model: type[GenericModel], **kwargs) -> list[GenericModel]: ...

    @overload
    def get_all(self, model: type[GenericDanbooruModel], to_model: None = None, **kwargs) -> list[GenericDanbooruModel]: ...

    def get_all(self,
                model: type[GenericDanbooruModel],
                to_model: type[GenericModel] | None = None,
                **kwargs,
                ) -> list[GenericDanbooruModel] | list[GenericModel]:

        object_list: list[GenericDanbooruModel] | list[GenericModel] = []
        return_model = to_model or model
        kwargs["page"] = 1

        assert (model_name := model.danbooru_model_name)
        kwargs["limit"] = 200 if model == models.DanbooruPost else 1000

        while True:
            logger.debug(f"Fetching all {model_name}s (page {kwargs["page"]})...")

            results = danbooru_api.danbooru_request("GET", f"{model_name}s.json", params=kwargs_to_include(**kwargs))
            object_list += [return_model(**r) for r in results]  # type: ignore[assignment]
            if len(results) < kwargs["limit"]:
                logger.info(f"Finished fetching {model_name}s. Total: {len(object_list)}")
                return object_list
            kwargs["page"] += 1

    def create_artist(self, name: str, other_names: list[str], urls: Sequence[Url | str]) -> None:
        url_string = self._generate_url_string_for_artist(urls)
        logger.info(f"Creating artist {name} with urls '{url_string}'")

        data = {
            "artist": {
                "name": name,
                "url_string": url_string,
                "other_names_string": " ".join(other_names),
            },
        }
        request = self.danbooru_request("POST", "artists.json", json=data)
        assert isinstance(request, dict) and request["id"]

    def update_artist_urls(self, artist: models.DanbooruArtist, urls: Sequence[Url | str]) -> None:
        url_string = self._generate_url_string_for_artist(urls, artist=artist)

        logger.info(f"Sending urls '{url_string}' to artist {artist}")

        data = {
            "artist": {
                "url_string": url_string,
            },
        }
        request = self.danbooru_request("PUT", f"{artist.model_path}.json", json=data)
        assert isinstance(request, dict) and request["success"] is True

    def _generate_url_string_for_artist(self, urls: Sequence[Url | str], artist: models.DanbooruArtist | None = None) -> str:
        parsed_urls = [Url.parse(url) for url in urls]
        normalized_urls: list[str] = []
        for url in parsed_urls:
            if isinstance(url, UselessUrl):
                continue
            try:
                normalized_urls.append(f"-{url.normalized_url}" if url.is_deleted else url.normalized_url)
            except (ReadTimeout, CloudflareChallengeError, RateLimitError):
                continue
            except ShieldedUrlError:
                normalized_urls.append(url.normalized_url)

        if artist:
            for url_data in artist._raw_data["urls"]:
                parsed = Url.parse(url_data["url"])
                if isinstance(parsed, UselessUrl):
                    continue
                try:
                    deleted = parsed.is_deleted if not isinstance(parsed, UnknownUrl) else (parsed.is_deleted or not url_data["is_active"])
                except (ReadTimeout, CloudflareChallengeError, ShieldedUrlError, RateLimitError):
                    deleted = url_data["is_active"]
                except Exception as e:
                    e.add_note(f"On {parsed}")
                    raise

                normalized_urls.append(f"-{parsed.normalized_url}" if deleted else parsed.normalized_url)

        return " ".join(normalized_urls)

    def update_post_tags(self, post: models.DanbooruPost, tags: list[str]) -> None:
        """Update a post's tags."""
        tag_string = " ".join(tags)
        logger.info(f"Sending tags {tag_string} to post {post.url}")
        data = {
            "post": {
                "tag_string": tag_string,
                "old_tag_string": "",
            },
        }
        response = self.danbooru_request("PUT", f"posts/{post.id}.json", json=data)
        assert isinstance(response, dict)

    def replace(self,
                post: models.DanbooruPost,
                replacement_file: File | None = None,
                replacement_url: Url | str | None = None,
                final_source: Url | str | None = None,
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

    def iqdb_search(self, *,
                    url: str | None = None,
                    file_path: Path | None = None,
                    min_similarity: int | None = None,
                    ) -> list[models.DanbooruIqdbMatch]:
        if url:
            sim_query = {"similarity": min_similarity} if min_similarity else {}
            data = {"url": url} | sim_query
            response = self.danbooru_request("GET", "iqdb_queries.json", params=data)
        elif file_path:
            headers = {"Content-type": "multipart/form-data"}
            files = {"search[file]": file_path.open("rb")}
            data = {"search[similarity]": min_similarity} if min_similarity else {}
            response = self.danbooru_request("POST", "iqdb_queries.json", headers=headers, files=files, data=data)
        else:
            raise ValueError("Either url or file_path must be present.")
        return [models.DanbooruIqdbMatch(**match) for match in response]

    def rename_user(self, user_id: int, new_name: str) -> None:
        data = {
            "user_id": user_id,
            "desired_name": new_name,
        }
        self.danbooru_request("POST", "user_name_change_requests", json=data)

    def ban_user(self, user_id: int, reason: str) -> dict:
        data = {
            "user_id": user_id,
            "duration": "P100Y",
            "reason": reason,
        }
        response = self.danbooru_request("POST", "bans", json=data)
        assert isinstance(response, dict)
        return response

    def create_forum_post(self, topic_id: int, body: str) -> None:
        data = {
            "forum_post": {
                "topic_id": topic_id,
                "body": body,
            },
        }
        response = self.danbooru_request("POST", "forum_posts.json", json=data)
        assert isinstance(response, dict) and response["id"]

    def create_bur(self, topic_id: int, script: str, reason: str) -> None:
        data = {
            "bulk_update_request": {
                "forum_topic_id": topic_id,
                "script": script,
                "reason": reason,
            },
        }
        response = self.danbooru_request("POST", "bulk_update_requests.json", json=data)
        assert isinstance(response, dict) and response["id"]

    def create_wiki_page(self, title: str, body: str) -> None:
        data = {
            "wiki_page": {
                "title": title,
                "body": body,
            },
        }
        response = self.danbooru_request("POST", "wiki_pages.json", json=data)
        assert isinstance(response, dict) and response["id"]

    @staticmethod
    def db_datetime(value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M:%SZ00")


def kwargs_to_include(**kwargs) -> dict:
    """Turn kwargs into url parameters that Rails can understand."""
    parameters = kwargs.copy()
    params = {}
    for named_parameter in ["only", "page", "limit"]:
        if n_p := parameters.pop(named_parameter, None):
            params[named_parameter] = n_p

    for _key, _value in parameters.items():
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
testbooru_api = DanbooruApi(domain="testbooru")
