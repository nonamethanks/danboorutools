from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.webtoons import (
    WebtoonsArtistNoLanguageUrl,
    WebtoonsArtistUrl,
    WebtoonsChapterUrl,
    WebtoonsUrl,
    WebtoonsWebtoonUrl,
)
from danboorutools.models.url import UselessUrl


class WebtoonsComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> WebtoonsUrl | UselessUrl | None:
        match parsable_url.url_parts:
            case language, genre, toon_title, "list" if len(language) == 2:
                return WebtoonsWebtoonUrl(parsed_url=parsable_url,
                                          language=language,
                                          genre=genre,
                                          toon_title=toon_title,
                                          toon_id=int(parsable_url.query["title_no"]))

            case "en", "search":
                return UselessUrl(parsed_url=parsable_url)

            case language, genre, toon_title, chapter_title, "viewer" if len(language) == 2:
                if chapter_id := parsable_url.query.get("episode_no"):
                    return WebtoonsChapterUrl(parsed_url=parsable_url,
                                              language=language,
                                              genre=genre,
                                              toon_title=toon_title,
                                              chapter_title=chapter_title,
                                              toon_id=int(parsable_url.query["title_no"]),
                                              chapter_id=int(chapter_id))
                else:
                    return WebtoonsWebtoonUrl(parsed_url=parsable_url,
                                              language=language,
                                              genre=genre,
                                              toon_title=toon_title,
                                              toon_id=int(parsable_url.query["title_no"]))

            case language, "creator", creator_id if len(language) == 2:
                return WebtoonsArtistUrl(parsed_url=parsable_url,
                                         language=language,
                                         creator_id=creator_id)

            case "creator", creator_id:
                return WebtoonsArtistNoLanguageUrl(parsed_url=parsable_url,
                                                   creator_id=creator_id)

            case language, genre, toon_title if len(language) == 2 and not parsable_url.query.get("title_no"):
                return UselessUrl(parsed_url=parsable_url)

            case _:
                return None
