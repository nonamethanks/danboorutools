from danboorutools.models.url import ArtistUrl, PostUrl, Url


class ThreadsUrl(Url):
    ...


class ThreadsArtistUrl(ArtistUrl, ThreadsUrl):
    username: str

    normalize_template = "https://www.threads.net/@{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class ThreadsPostUrl(PostUrl, ThreadsUrl):
    post_id: str
    username: str

    normalize_template = "https://www.threads.net/@{username}/post/{post_id}"
