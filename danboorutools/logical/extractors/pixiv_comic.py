from danboorutools.models.url import GalleryUrl, PostAssetUrl, PostUrl, Url


class PixivComicUrl(Url):
    pass


class PixivComicStoryUrl(PostUrl, PixivComicUrl):
    story_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        story_id = kwargs["story_id"]
        return f"https://comic.pixiv.net/viewer/stories/{story_id}"


class PixivComicWorkUrl(GalleryUrl, PixivComicUrl):
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        return f"https://comic.pixiv.net/works/{post_id}"


class PixivComicImageUrl(PostAssetUrl, PixivComicUrl):
    ...
