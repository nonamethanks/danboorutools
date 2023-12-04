from danboorutools.models.url import GalleryUrl, PostUrl, Url


class GoogleDriveUrl(Url):
    ...


class GoogleDriveFolderUrl(GalleryUrl, GoogleDriveUrl):
    folder_id: str

    normalize_template = "https://drive.google.com/drive/folders/{folder_id}"


class GoogleDriveFileUrl(PostUrl, GoogleDriveUrl):
    file_id: str

    normalize_template = "https://drive.google.com/file/d/{file_id}/view"
