from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pykakasi
import unidecode
from cloudscraper.exceptions import CloudflareChallengeError
from py_trans import PyTranslator
from pydantic import ValidationError
from requests.exceptions import ReadTimeout

from danboorutools import logger
from danboorutools.exceptions import DeadUrlError, RateLimitError
from danboorutools.logical.progress_tracker import ProgressTracker
from danboorutools.logical.sessions.ascii2d import Ascii2dArtistResult, Ascii2dSession
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.logical.sessions.saucenao import SaucenaoArtistResult, SaucenaoSession
from danboorutools.logical.urls.facebook import FacebookMediaSetUrl
from danboorutools.logical.urls.google_drive import GoogleDriveFileUrl
from danboorutools.logical.urls.instagram import InstagramUrl
from danboorutools.logical.urls.nicovideo import NicovideoVideoUrl
from danboorutools.logical.urls.pixiv import PixivImageUrl
from danboorutools.logical.urls.steamcommunity import SteamcommunityFileUrl
from danboorutools.logical.urls.twitch import TwitchVideoUrl
from danboorutools.logical.urls.youtube import YoutubePlaylistUrl, YoutubeVideoUrl
from danboorutools.models.url import ArtistUrl, GalleryUrl, InfoUrl, RedirectUrl, UnknownUrl, UnsupportedUrl, Url, UselessUrl

if TYPE_CHECKING:
    from danboorutools.models.danbooru import DanbooruArtist, DanbooruPost


class DuplicateArtistOnDanbooruError(Exception):
    def __init__(self, duplicate_url: Url, artists: list[DanbooruArtist]) -> None:
        self.duplicate_url = duplicate_url
        self.artists = artists

        self.message = f"The following artists share the url {duplicate_url.normalized_url}: {", ".join(a.url for a in artists)}"
        super().__init__(self.message)


class ArtistFinder:
    kakasi = pykakasi.kakasi()
    translator = PyTranslator()

    # TODO: should rename all user_123 artists to a proper extracted name
    def __init__(self) -> None:
        self.skipped_posts: ProgressTracker[list[int]] = ProgressTracker("CREATE_ARTIST_TAGS_SKIPPED_POSTS", [])
        self.saucenao = SaucenaoSession()
        self.ascii2d = Ascii2dSession()

    @classmethod
    def update_artist_urls(cls, artist_id: int) -> None:
        artist, = danbooru_api.artists(id=artist_id)
        urls = cls.find_all_related_urls(*artist.urls)
        danbooru_api.update_artist_urls(artist=artist, urls=urls)

    def create_or_tag_artist_for_post(self, post: DanbooruPost, retry_skipped: bool = False) -> bool:
        if not isinstance((source := post.source), Url):
            raise TypeError(source)

        if not retry_skipped and post.id in self.skipped_posts.value:
            return False

        logger.info(f"Extracting artist for post {post}, source {source}")
        try:
            artist_url = source.artist
        except DeadUrlError:
            artist_url = None
            logger.debug(f"{source} for post {post} is deleted.")
            result_from_archives = self.search_for_artist_in_archives(post)
            if not result_from_archives:
                logger.error(f"Couldn't extract an artist for post {post}.")
                self.skipped_posts.value = [*self.skipped_posts.value, post.id]

                assert source.is_deleted
                danbooru_api.update_post_tags(post, ["bad_id"])
                return False
        else:
            assert artist_url
            logger.debug(f"Found artist url {artist_url} for source {source} for post {post}")
            result_from_archives = None
            if artist_url.is_deleted:
                # still check saucenao/ascii2d for more data
                try:
                    result_from_archives = self.search_for_artist_in_archives(post)
                except Exception as e:
                    e.add_note(f"On post: {post}, artist: {artist_url}")
                    raise

        try:
            artist_tag = self._find_or_create_artist_tag(artist_url, result_from_archives)
        except DuplicateArtistOnDanbooruError as e:
            self.post_duplicate_on_forums(post=post, duplicate_url=e.duplicate_url, artists=e.artists)
            self.skipped_posts.value = [*self.skipped_posts.value, post.id]
            return False
        except Exception as e:
            e.add_note(f"On post: {post}, artist: {artist_url}, archived result: {result_from_archives}")
            raise

        tags_to_send = ["-artist_request", artist_tag]
        if not isinstance(source, PixivImageUrl) and source.is_deleted: # could be revision
            tags_to_send += ["bad_id"]

        danbooru_api.update_post_tags(post, tags_to_send)
        return True

    def _find_or_create_artist_tag(self,
                                   artist_url: ArtistUrl | None,
                                   result_from_archives: Ascii2dArtistResult | SaucenaoArtistResult | None,
                                   ) -> str:
        found_artist_urls = []
        if artist_url:
            found_artist_urls += self.find_all_related_urls(artist_url)
        if result_from_archives:
            found_artist_urls += self.find_all_related_urls(*result_from_archives.found_urls)

        if (artist_tag := self.find_artist_tag(found_artist_urls)):
            return artist_tag

        primary_names, secondary_names = [], []
        for url_with_names in [url for url in found_artist_urls if isinstance(url, InfoUrl)]:
            try:
                url_primary_names = url_with_names.primary_names
            except ReadTimeout:
                continue
            except Exception as e:
                e.add_note(f"While extracting primary names from {url_with_names}...")
                raise
            try:
                url_secondary_names = url_with_names.secondary_names
            except ReadTimeout:
                continue

            # ensure no stray `None`s or empty strings made their way here
            assert all(url_primary_names) and all(url_secondary_names), (url_with_names, url_primary_names, url_secondary_names)
            primary_names += url_primary_names
            secondary_names += [name for name in url_secondary_names if name not in primary_names]

        if result_from_archives:
            primary_names = result_from_archives.primary_names + primary_names
            secondary_names = result_from_archives.secondary_names + secondary_names

        return self.create_artist_tag(primary_names, secondary_names, found_artist_urls)

    def search_for_artist_in_archives(self, post: DanbooruPost) -> SaucenaoArtistResult | Ascii2dArtistResult | None:
        if post.file_ext in ["mp4", "webm", "swf"]:
            logger.debug(f"Skipping reverse searching {post} because it's a video.")
            return None

        if post.media_asset.image_width > 10_000 or post.media_asset.image_height > 10_000:
            logger.debug(f"Skipping reverse searching {post} on Ascii2D because it's too big.")
        else:
            logger.debug("Checking Ascii2d...")
            result = self.ascii2d.find_gallery(post.file_url, original_url=post.source, original_post=post)
            if result:
                logger.debug(f"Extracted {result} for {post} from Ascii2d")
                return result

            logger.debug("No result from Ascii2d. Checking Saucenao...")

        result = self.saucenao.find_gallery(post.file_url, original_url=post.source, original_post=post)
        if result:
            logger.debug(f"Extracted {result} for {post} from Saucenao")
            return result

        logger.debug(f"Couldn't extract an artist for post {post} from saucenao or ascii2d")
        return None

    @classmethod
    def find_all_related_urls(cls, *urls: InfoUrl) -> list[InfoUrl | GalleryUrl]:
        found_artist_urls: list[GalleryUrl | InfoUrl | UnknownUrl] = []
        for url in urls:
            found_artist_urls += [u for u in cls.extract_related_urls_recursively(url, found_artist_urls) if u not in found_artist_urls]

        if unknown := list(filter(lambda x: isinstance(x, UnknownUrl), found_artist_urls)):
            raise NotImplementedError(unknown)

        logger.debug(f"Found urls: {", ".join(map(str, found_artist_urls))}")
        return found_artist_urls  # type: ignore[return-value] # false positive

    @classmethod
    def extract_related_urls_recursively(cls,
                                         first_url: InfoUrl,
                                         scanned_urls: list | None = None,
                                         ) -> list[InfoUrl | GalleryUrl | UnknownUrl]:

        scanned_urls = scanned_urls or []
        if first_url in scanned_urls:
            return scanned_urls

        logger.debug(f"Crawling {first_url}...")
        scanned_urls += [first_url]

        try:
            if first_url.is_deleted:
                return list(dict.fromkeys(scanned_urls))
        except (ReadTimeout, CloudflareChallengeError):
            return list(dict.fromkeys(scanned_urls))
        except RateLimitError:
            if isinstance(first_url, InstagramUrl):
                return list(dict.fromkeys(scanned_urls))
            raise
        except ValidationError as e:
            e.add_note(f"While crawling url {first_url}...")
            raise

        try:
            related_urls = first_url.related
        except Exception as e:
            e.add_note(f"While crawling url {first_url}...")
            raise

        assert all(isinstance(u, Url) for u in related_urls), f"{first_url} returned a string instead of an url for .related. Uh oh!"

        for related_url in related_urls:
            if related_url in scanned_urls:
                continue

            if related_url.parsed_url.domain in ["t.me", "tiktok.com"]:
                logger.debug(f"Found blacklisted url {related_url}; skipping...")
                continue

            logger.debug(f"Found {related_url} while crawling {first_url}...")

            if isinstance(related_url, RedirectUrl):
                try:
                    related_url = related_url.resolved  # noqa: PLW2901
                    logger.debug(f"It was resolved into {related_url}...")
                except (DeadUrlError, ReadTimeout) as e:
                    logger.debug(f"Couldn't resolve url {related_url} because of an exception ({e}), skipping...")
                    continue

            if isinstance(related_url, UnknownUrl) and related_url.parsed_url.is_base_url:
                logger.debug("Skipping because it's a basic url...")
                continue
            if isinstance(related_url, UselessUrl):
                logger.debug("Skipping because it's a useless url...")
                continue

            if isinstance(related_url, YoutubeVideoUrl | YoutubePlaylistUrl | NicovideoVideoUrl):
                logger.debug(f"Skipping {related_url} because it has a high chance of being a random video.")
                continue

            if isinstance(related_url, GoogleDriveFileUrl | SteamcommunityFileUrl):
                logger.debug(f"Skipping {related_url} because it has a high chance of being a random file.")
                continue

            if isinstance(related_url, TwitchVideoUrl | FacebookMediaSetUrl):
                logger.debug(f"Skipping {related_url} because artist extraction is not feasible.")
                continue

            if isinstance(related_url, UnsupportedUrl):
                logger.debug(f"Skipping {related_url} because it's an unsupported url...")
                continue

            if isinstance(related_url, UnknownUrl) and not cls.is_url_worth_implementing(related_url):
                logger.debug(f"Skipping {related_url} because it's an unknown url and there's too few results on danbooru to implement it.")
                continue

            if not isinstance(related_url, InfoUrl):
                try:
                    related_url = related_url.artist  # noqa: PLW2901
                except DeadUrlError:
                    logger.debug("It's deleted and not a valid url; skipping...")
                    continue
                else:
                    logger.debug(f"It was resolved into {related_url}...")

            scanned_urls += cls.extract_related_urls_recursively(related_url, scanned_urls)
            scanned_urls.append(related_url)

        return list(dict.fromkeys(scanned_urls))

    @staticmethod
    def find_artist_tag(artist_urls: list[InfoUrl | GalleryUrl]) -> str | None:
        logger.debug("Searching on danbooru for an existing artist tag...")
        for url in artist_urls:
            results = danbooru_api.artists(url_matches=url.parsed_url.raw_url)
            if results:

                if len(results) > 1:
                    raise DuplicateArtistOnDanbooruError(duplicate_url=url, artists=results)

                result, = results
                if result.tag.category_name != "artist":
                    raise NotImplementedError(f"{result} is not an artist tag!")
                danbooru_api.update_artist_urls(artist=result, urls=artist_urls)
                logger.debug(f"Found existing artist {result}.")
                return result.tag.name

        logger.debug("Found no matching artist on danbooru.")
        return None

    @classmethod
    def create_artist_tag(cls, primary_names: list[str], secondary_names: list[str], found_artist_urls: list[GalleryUrl | InfoUrl]) -> str:
        final_tag_name = cls.decide_new_artist_tag_name(primary_names, secondary_names)

        other_names = [u.replace(" ", "_") for u in primary_names if u != final_tag_name]
        danbooru_api.create_artist(name=final_tag_name, other_names=other_names, urls=found_artist_urls)
        logger.info(f"Artist tag {final_tag_name} created.")

        return final_tag_name

    @classmethod
    def decide_new_artist_tag_name(cls, primary_names: list[str], secondary_names: list[str]) -> str:
        primary_names = [cls.sanitize_tag_name(name) for name in list(dict.fromkeys(primary_names))]
        secondary_names = [cls.sanitize_tag_name(name) for name in list(dict.fromkeys(secondary_names))
                           if cls.sanitize_tag_name(name) not in primary_names]
        secondary_names.sort(key=lambda x: x.startswith("user_"))  # put bad pixiv qualifiers as last choiec

        attempts = []

        for candidate in primary_names:
            if cls.valid_new_tag_name(candidate):
                return candidate
            else:
                attempts.append(candidate)

        combinations = list(dict.fromkeys(
            (name, qualifier)
            for name in primary_names
            for qualifier in primary_names + secondary_names
            if name != qualifier
        ))

        for name, qualifier in combinations:
            candidate = cls.sanitize_tag_name(f"{name}_({qualifier})")
            if cls.valid_new_tag_name(candidate):
                return candidate
            else:
                attempts.append(candidate)

        for candidate in secondary_names:
            if cls.valid_new_tag_name(candidate):
                return candidate
            else:
                attempts.append(candidate)

        raise NotImplementedError(f"Couldn't figure out an artist name for {attempts}")

    @classmethod
    def sanitize_tag_name(cls, potential_tag: str) -> str:
        potential_tag = re.split(r"[@＠🔞]", potential_tag)[0]  # japanese artists love this shit too much

        if not re.match("^[\x00-\x7F]+$", potential_tag):
            potential_tag = cls.romanize_tag_name(potential_tag)

        allowed_characters = "-_()"
        candidate = "".join([c if c.isalnum() or c in allowed_characters else "_" for c in potential_tag])  # strip all non-basic characters

        candidate = candidate.replace("(", "_(").replace(")", ")_")  # add underscore before parenthesis
        candidate = re.sub(r"_+", "_", candidate)                    # merge multiple underscores
        candidate = candidate.replace("(_", "(").replace("_)", ")")  # remove underscores inside parentheses
        candidate = candidate.strip("_(-").strip()                   # strip underscores, hyphens and parentheses from end of string
        candidate = re.sub(r"_?\(\)", "", candidate)

        return candidate.lower()

    @classmethod
    def romanize_tag_name(cls, potential_tag: str) -> str:
        language = cls.translator.detect(potential_tag)
        translated_results = cls.kakasi.convert(potential_tag)

        if len(translated_results) == 1 and translated_results[0]["orig"].strip() == potential_tag.strip():
            # single japanese word
            candidate = translated_results[0]["passport"]
        elif language == "ja":
            candidate = "_".join(k["passport"] for k in translated_results)
        else:
            # chinese, korean, etc
            candidate = potential_tag

        return unidecode.unidecode(candidate)

    @staticmethod
    def valid_new_tag_name(potential_tag: str) -> bool:
        if len(potential_tag) < 5:
            return False

        if potential_tag.startswith("-"):
            return False

        for pair in ["()", "[]"]:
            if not any(c in potential_tag for c in pair):
                continue
            if len([c for c in potential_tag if c == pair[0]]) != len([c for c in potential_tag if c == pair[1]]):
                return False

        return not danbooru_api.tags(name=potential_tag)

    @classmethod
    def is_url_worth_implementing(cls, url: UnknownUrl) -> bool:
        url_results = danbooru_api.artists(url_matches=f"*{url.parsed_url.domain}*", limit=100)
        return len(url_results) > 40

    def post_duplicate_on_forums(self, post: DanbooruPost, duplicate_url: Url, artists: list[DanbooruArtist]) -> None:
        assert len(artists) > 1  # you never know lmao
        logger.info("Sending duplicate message to forums...")
        message = f"During an automated scan to determine the author of post #{post.id}, "
        message += "the following artists were found to have a duplicate url:"
        for artist in sorted(artists, key=lambda x: x.id):
            message += f"\n* artist #{artist.id} ([[{artist.name}]])"
        message += f"\n\nThe duplicate url is {duplicate_url.normalized_url}.\n"
        message += "This post will be skipped on subsequent scans.\n"
        message += "Please merge these artists if appropriate, and assign the correct artist to the post manually."
        logger.info(message)

        raise NotImplementedError(message)
        # danbooru_api.create_forum_post(topic_id=os.environ["DANBOORU_ARTIST_TOPIC_ID"], body=message)
