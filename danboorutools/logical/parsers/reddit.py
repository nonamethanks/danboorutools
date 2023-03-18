from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.extractors.reddit import RedditPostUrl, RedditUrl, RedditUserUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class RedditComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> RedditUrl | None:
        instance: RedditUrl

        match parsable_url.url_parts:
            # http://www.reddit.com/r/Kappa/comments/34d761/shirt_idea_for_alex_myers_sponsorship/cqu5yc3
            # https://www.reddit.com/r/Overwatch/comments/4zjb8t/kunoichi_widowmaker_concept_art/
            # https://www.reddit.com/r/Overwatch/comments/4zjb8t
            case "r", subreddit, "comments", post_id, *title:
                instance = RedditPostUrl(parsable_url)
                instance.subreddit = subreddit
                instance.post_id = post_id
                if len(title) == 1:
                    [instance.title] = title
                elif len(title) == 2:
                    [instance.title, instance.second_post_id] = title
                elif title:
                    raise NotImplementedError(parsable_url)

            # https://www.reddit.com/user/blank_page_drawings/comments/nfjz0d/a_sleepy_orc/
            # https://www.reddit.com/user/blank_page_drawings/comments/nfjz0d
            case ("user" | "u"), username, "comments", post_id, *title:
                instance = RedditPostUrl(parsable_url)
                instance.username = username
                instance.post_id = post_id
                if title:
                    [instance.title] = title

            # https://old.reddit.com/user/Ok-Aerie-1683/submitted/
            case ("user" | "u"), username, "submitted":
                instance = RedditUserUrl(parsable_url)
                instance.username = username

            # https://www.reddit.com/comments/ttyccp
            # https://www.reddit.com/gallery/ttyccp
            case ("comments" | "gallery"), post_id, :
                instance = RedditPostUrl(parsable_url)
                instance.post_id = post_id

            # http://www.reddit.com/user/TouchFluffyTailss/
            case ("user" | "u"), username:
                instance = RedditUserUrl(parsable_url)
                instance.username = username

            case "r", _:  # no point in even acknowledging subreddits. they'll make a mess of the crawler otherwise
                raise UnparsableUrlError(parsable_url)

            # https://www.reddit.com/ttyccp
            case post_id, :
                instance = RedditPostUrl(parsable_url)
                instance.post_id = post_id

            case _:
                return None

        return instance
