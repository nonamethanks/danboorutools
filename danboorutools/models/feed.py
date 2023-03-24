from danboorutools.logical.sessions import Session
from danboorutools.models.has_posts import HasPosts


class Feed(HasPosts):
    session = Session()

    quit_early_page = 3

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"
