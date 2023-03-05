import re

import pykakasi
import unidecode

from danboorutools import logger
from danboorutools.exceptions import UrlIsDeleted
from danboorutools.logical.sessions.ascii2d import Ascii2dArtistResult, Ascii2dSession
from danboorutools.logical.sessions.danbooru import danbooru_api
from danboorutools.logical.sessions.saucenao import SaucenaoArtistResult, SaucenaoSession
from danboorutools.models.danbooru import DanbooruPost
from danboorutools.models.url import GalleryUrl, InfoUrl, RedirectUrl, UnknownUrl, Url
from danboorutools.scripts import ProgressTracker


class ArtistFinder:
    kakasi = pykakasi.kakasi()

    # TODO: should rename all user_123 artists to a proper extracted name
    def __init__(self) -> None:
        self.skipped_posts: ProgressTracker[list[int]] = ProgressTracker("CREATE_ARTIST_TAGS_SKIPPED_POSTS", [])
        self.saucenao = SaucenaoSession()
        self.ascii2d = Ascii2dSession()

    def create_or_tag_artist_for_post(self, post: DanbooruPost) -> bool:
        assert isinstance((source := post.source), Url)

        if post.id in self.skipped_posts.value:
            return False

        logger.info(f"Extracting artist for post {post}, source {source}")
        try:
            artist_url = source.artist
            logger.debug(f"Found artist url {artist_url} for source {source} for post {post}")
            result_from_archives = None
        except UrlIsDeleted:
            artist_url = None
            logger.debug(f"{source} for post {post} is deleted.")
            result_from_archives = self.search_for_artist_in_archives(post)
            if not result_from_archives:
                self.skipped_posts.value = self.skipped_posts.value + [post.id]
                return False

        if artist_url:
            found_artist_urls = self.find_all_related_urls(artist_url)
        elif result_from_archives:
            found_artist_urls = self.find_all_related_urls(result_from_archives.primary_url, *result_from_archives.extra_urls)
        artist_tag = self.find_artist_tag(found_artist_urls)

        if not artist_tag:
            urls_with_names = [u for u in found_artist_urls if isinstance(u, InfoUrl)]
            primary_names = [name for found_url in urls_with_names for name in found_url.primary_names]
            secondary_names = [name for found_url in urls_with_names for name in found_url.secondary_names if name not in primary_names]
            if result_from_archives:
                primary_names = result_from_archives.primary_names + primary_names
                secondary_names = result_from_archives.secondary_names + secondary_names

            artist_tag = self.create_artist_tag(primary_names, secondary_names, found_artist_urls)

        danbooru_api.update_post_tags(post, ["-artist_request", artist_tag])
        return True

    def search_for_artist_in_archives(self, post: DanbooruPost) -> SaucenaoArtistResult | Ascii2dArtistResult | None:
        logger.debug("Checking Saucenao...")
        result = self.saucenao.find_gallery(post.file_url, original_url=post.source, original_post=post)
        if result:
            logger.debug(f"Extracted {result} for {post} from Saucenao")
            return result

        logger.debug("No result from Saucenao. Checking Ascii2d...")
        result = self.ascii2d.find_gallery(post.file_url, original_url=post.source, original_post=post)  # type: ignore[assignment]
        if result:
            logger.debug(f"Extracted {result} for {post} from Ascii2d")
            return result

        logger.error(f"Couldn't extract an artist for post {post}")
        return None

    @classmethod
    def find_all_related_urls(cls, *urls: InfoUrl) -> list[InfoUrl | GalleryUrl]:
        found_artist_urls: list[GalleryUrl | InfoUrl | UnknownUrl] = []
        for url in urls:
            found_artist_urls += cls.extract_related_urls_recursively(url, found_artist_urls)

        if unknown := list(filter(lambda x: isinstance(x, UnknownUrl), found_artist_urls)):
            raise NotImplementedError(unknown)
        logger.debug(f"Found urls: {', '.join(map(str, found_artist_urls))}")

        return found_artist_urls  # type: ignore[return-value] # false positive

    @classmethod
    def extract_related_urls_recursively(cls,
                                         first_url: InfoUrl,
                                         scanned_urls: list | None = None
                                         ) -> list[InfoUrl | GalleryUrl | UnknownUrl]:

        scanned_urls = scanned_urls or []
        if first_url in scanned_urls:
            return scanned_urls

        logger.debug(f"Crawling {first_url}...")
        scanned_urls += [first_url]

        if first_url.is_deleted:
            return list(dict.fromkeys(scanned_urls))

        try:
            related_urls = first_url.related
        except Exception as e:
            e.add_note(f"While crawling url {first_url}...")
            raise

        for related_url in related_urls:
            if related_url in scanned_urls:
                continue

            logger.debug(f"Found {related_url} while crawling {first_url}...")

            if isinstance(related_url, RedirectUrl):
                try:
                    related_url = related_url.resolved
                    logger.debug(f"It was resolved into {related_url}...")
                except UrlIsDeleted:
                    logger.debug(f"Couldn't resolve url {related_url} because it was dead, skipping...")
                    continue

            if isinstance(related_url, InfoUrl):
                scanned_urls += cls.extract_related_urls_recursively(related_url, scanned_urls)
            else:
                raise NotImplementedError(related_url)

            if isinstance(related_url, (GalleryUrl, UnknownUrl)):  # wip
                scanned_urls.append(related_url)

        return list(dict.fromkeys(scanned_urls))

    @staticmethod
    def find_artist_tag(artist_urls: list[InfoUrl | GalleryUrl]) -> str | None:
        logger.debug("Searching on danbooru for an existing artist tag...")
        for url in artist_urls:
            results = danbooru_api.artists(url_matches=url.parsed_url.raw_url)
            if results:
                assert len(results) == 1, results  # TODO: post in the forums in case there's more than one artist
                result, = results
                if result.tag.category_name != "artist":
                    raise NotImplementedError(f"{result} is not an artist tag!")
                danbooru_api.update_artist_urls(artist=result, urls=artist_urls)
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
        primary_names = list(dict.fromkeys(primary_names))
        secondary_names = [n for n in list(dict.fromkeys(secondary_names)) if n not in primary_names]

        for primary_name in primary_names:
            candidate = cls.sanitize_tag_name(primary_name)
            if cls.valid_new_tag_name(candidate):
                return candidate

        combinations = [
            (name, qualifier)
            for name in primary_names
            for qualifier in primary_names + secondary_names
            if name != qualifier
        ]
        for name, qualifier in combinations:
            name = cls.sanitize_tag_name(name)
            qualifier = cls.sanitize_tag_name(qualifier)

            candidate = cls.sanitize_tag_name(f"{name}_({qualifier})")
            if cls.valid_new_tag_name(candidate):
                return candidate

        raise NotImplementedError

    @classmethod
    def sanitize_tag_name(cls, potential_tag: str) -> str:
        if not re.match("^[\x00-\x7F]+$", potential_tag):
            potential_tag = cls.romanize_tag_name(potential_tag)

        allowed_characters = "-_()"
        candidate = "".join([c if c.isalnum() or c in allowed_characters else "_" for c in potential_tag])  # strip all non-basic characters

        candidate = candidate.replace("(", "_(").replace(")", ")_")  # add underscore before parenthesis
        candidate = re.sub(r"_+", "_", candidate)                    # merge multiple underscores
        candidate = candidate.replace("(_", "(").replace("_)", ")")  # remove underscores inside parentheses
        candidate = candidate.strip("_(").strip()  # strip underscores and parentheses from end of string

        return candidate

    @classmethod
    def romanize_tag_name(cls, potential_tag: str) -> str:
        translated_results = cls.kakasi.convert(potential_tag)

        if len(translated_results) == 1 and translated_results[0]["orig"].strip() == potential_tag.strip():
            # single japanese word
            candidate = translated_results[0]["passport"]
        elif "".join([k["orig"] for k in translated_results]) == potential_tag and all(k["passport"] for k in translated_results):
            # multiple japanese words
            candidate = "_".join(k["passport"] for k in translated_results)
        else:
            # chinese, korean, etc
            candidate = potential_tag

        return unidecode.unidecode(candidate)

    @staticmethod
    def valid_new_tag_name(potential_tag: str) -> bool:
        if len(potential_tag) <= 5:
            return False

        for pair in ["()", "[]"]:
            if not any(c in potential_tag for c in pair):
                continue
            if len([c for c in potential_tag if c == pair[0]]) != len([c for c in potential_tag if c == pair[1]]):
                return False

        return not danbooru_api.tags(name=potential_tag)
