from danboorutools.logical.sessions.reddit import RedditSession
from danboorutools.models.url import ArtistUrl, Url


class RedditUrl(Url):
    session = RedditSession()


class RedditUserUrl(ArtistUrl, RedditUrl):
    username: str

    normalize_string = "https://www.reddit.com/user/{username}"

    @property
    def primary_names(self) -> list[str]:
        return [self.username]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return self.session.get_social_links(self.username)


class RedditPostUrl(ArtistUrl, RedditUrl):
    subreddit: str | None = None
    username: str | None = None

    post_id: str
    title: str | None = None

    second_post_id: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        subreddit = kwargs.get("subreddit")
        username = kwargs.get("username")
        post_id = kwargs["post_id"]
        title = kwargs.get("title")

        if subreddit and post_id and title:
            if second_post_id := kwargs.get("second_post_id"):
                return f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/{title}/{second_post_id}"
            else:
                return f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/{title}"
        elif subreddit and post_id:
            return f"https://www.reddit.com/r/{subreddit}/comments/{post_id}"
        elif username and post_id and title:
            return f"https://www.reddit.com/user/{username}/comments/{post_id}/{title}"
        elif username and post_id:
            return f"https://www.reddit.com/user/{username}/comments/{post_id}"
        elif post_id:
            return f"https://www.reddit.com/comments/{post_id}"
        else:
            raise NotImplementedError(kwargs)
