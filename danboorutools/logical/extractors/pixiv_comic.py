from danboorutools.models.url import GalleryUrl, PostUrl, Url


class PixivComicUrl(Url):
    pass


class PixivComicStoryUrl(PostUrl, PixivComicUrl):
    story_id: int

    normalize_template = "https://comic.pixiv.net/viewer/stories/{story_id}"


class PixivComicWorkUrl(GalleryUrl, PixivComicUrl):
    post_id: int

    normalize_template = "https://comic.pixiv.net/works/{post_id}"
