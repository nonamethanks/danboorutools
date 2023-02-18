from danboorutools.models.url import GalleryUrl, PostAssetUrl, PostUrl, Url


class PixivComicUrl(Url):
    pass


class PixivComicStoryUrl(PostUrl, PixivComicUrl):
    normalization = "https://comic.pixiv.net/viewer/stories/{story_id}"

    story_id: int


class PixivComicWorkUrl(GalleryUrl, PixivComicUrl):
    normalization = "https://comic.pixiv.net/works/{work_id}"

    work_id: int


class PixivComicImageUrl(PostAssetUrl, PixivComicUrl):
    ...
