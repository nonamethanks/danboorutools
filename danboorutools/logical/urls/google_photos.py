from danboorutools.models.url import GalleryUrl, PostUrl, Url


class GooglePhotosUrl(Url):
    ...


class GooglePhotosFolderUrl(GalleryUrl, GooglePhotosUrl):
    folder_id: str
    folder_key: str

    normalize_template = "https://photos.google.com/share/{folder_id}?key={folder_key}"


class GooglePhotosPhotoUrl(PostUrl, GooglePhotosUrl):
    photo_id: str
