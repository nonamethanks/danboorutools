from danboorutools.models.url import ArtistUrl, PostUrl, Url


class TwitchUrl(Url):
    ...


class TwitchChannelUrl(ArtistUrl, TwitchUrl):
    username: str

    normalize_template = "https://twitch.tv/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []  # too much of a headache


class TwitchVideoUrl(PostUrl, TwitchUrl):
    video_id: int

    normalize_template = "https://twitch.tv/videos/{video_id}"
