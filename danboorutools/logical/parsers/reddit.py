from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.reddit import RedditPostUrl, RedditUrl, RedditUserUrl


class RedditComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> RedditUrl | None:
        match parsable_url.url_parts:
            # http://www.reddit.com/r/Kappa/comments/34d761/shirt_idea_for_alex_myers_sponsorship/cqu5yc3
            # https://www.reddit.com/r/Overwatch/comments/4zjb8t/kunoichi_widowmaker_concept_art/
            # https://www.reddit.com/r/Overwatch/comments/4zjb8t
            case "r", subreddit, "comments", post_id, *title_parts:

                if not title_parts:
                    title = None
                    second_post_id = None
                elif len(title_parts) == 1:
                    [title] = title_parts
                    second_post_id = None
                elif len(title_parts) == 2:
                    [title, second_post_id] = title_parts
                elif title_parts:
                    raise NotImplementedError(parsable_url)

                return RedditPostUrl(parsed_url=parsable_url,
                                     subreddit=subreddit,
                                     post_id=post_id,
                                     title=title,
                                     second_post_id=second_post_id)

            # https://www.reddit.com/user/blank_page_drawings/comments/nfjz0d/a_sleepy_orc/
            # https://www.reddit.com/user/blank_page_drawings/comments/nfjz0d
            case ("user" | "u"), username, "comments", post_id, *title_parts:
                title, = title_parts if title_parts else [None]  # type: ignore[list-item]
                return RedditPostUrl(parsed_url=parsable_url,
                                     username=username,
                                     post_id=post_id,
                                     title=title)

            # https://old.reddit.com/user/Ok-Aerie-1683/submitted/
            case ("user" | "u"), username, "submitted":
                return RedditUserUrl(parsed_url=parsable_url,
                                     username=username)

            # https://www.reddit.com/comments/ttyccp
            # https://www.reddit.com/gallery/ttyccp
            case ("comments" | "gallery"), post_id, :
                return RedditPostUrl(parsed_url=parsable_url,
                                     post_id=post_id)

            # http://www.reddit.com/user/TouchFluffyTailss/
            case ("user" | "u"), username:
                return RedditUserUrl(parsed_url=parsable_url,
                                     username=username)

            case "r", _:  # no point in even acknowledging subreddits. they'll make a mess of the crawler otherwise
                raise UnparsableUrlError(parsable_url)

            # https://www.reddit.com/ttyccp
            case post_id, :
                return RedditPostUrl(parsed_url=parsable_url,
                                     post_id=post_id)

            case _:
                return None
