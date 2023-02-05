from functools import cached_property

from danboorutools.exceptions import DownloadError, EHEntaiRateLimit, UnknownUrlError
from danboorutools.logical.sessions.ehentai import EHentaiSession
from danboorutools.models.file import ArchiveFile, File
from danboorutools.models.url import AssetUrl, GalleryUrl, PostUrl, Url
from danboorutools.util import compile_url

BASE_DOMAIN = compile_url(r"(?:g\.)?(?P<subdomain>e(?:-|x)hentai)\.org")
GALLERY_PATTERN = compile_url(BASE_DOMAIN, r"\/g\/(?P<gallery_id>\d+)\/(?P<gallery_token>\w+)")
PAGE_PATTERN = compile_url(BASE_DOMAIN, r"\/s\/(?P<page_token>\w+)\/(?P<gallery_id>\d+)-(?P<page_number>\d+)")
THUMBNAIL_PATTERN = compile_url(r"ehgt\.org\/\w{2}\/\w{2}\/(?P<page_token>\w{10})[\w-]+\.\w+")
PAGE_DOWNLOAD_PATTERN = compile_url(BASE_DOMAIN, r"\/fullimg\.php\?gid=(?P<gallery_id>\d+)&page=(?P<page_number>\d+)&key=\w+")
IMAGE_DIRECT_PATTERN = compile_url(
    r".*\.hath\.network:\d+\/h\/[\w-]+\/keystamp=[\w-]+;fileindex=\d+;xres=(?P<sample_size>\d+)\/(?P<filename>\w+)\.\w+"
)


class EHentaiUrl(Url):
    session = EHentaiSession()
    domains = ["e-hentai.org", "exhentai.org", "ehgt.org", "hath.network"]


class EHentaiImageUrl(EHentaiUrl, AssetUrl):
    patterns = {
        THUMBNAIL_PATTERN: None,
        PAGE_DOWNLOAD_PATTERN: None,
        IMAGE_DIRECT_PATTERN: None,
    }


class EHentaiPageUrl(EHentaiUrl, PostUrl["EHentaiGalleryUrl", EHentaiImageUrl]):
    assets: list["EHentaiImageUrl"]
    patterns = {PAGE_PATTERN: "https://{subdomain}.org/s/{page_token}/{gallery_id}-{page_number}"}

    @cached_property
    def gallery(self) -> "EHentaiGalleryUrl":
        gallery_token = self.session.get_gallery_token_from_page_data(**self.properties)
        return self.build(url_type=EHentaiGalleryUrl,
                          gallery_token=gallery_token,
                          gallery_id=self.properties["gallery_id"],
                          subdomain=self.properties["subdomain"])

    def extract_assets(self) -> None:
        self.session.browser_login()
        asset_url = self._get_direct_url()
        asset_url.download_files()
        self.assets = [asset_url]

    def _get_direct_url(self) -> EHentaiImageUrl:
        browser = self.session.browser
        browser.get(self.normalized_url)
        get_original_el = browser.find_elements_by_text("Download original", full_match=False)
        if get_original_el:
            asset_url = get_original_el[0].get_attribute("href")
        else:
            asset_url = browser.find_element_by_css_selector("img#img").get_attribute("src")

        asset_url_parsed = self.parse(asset_url)
        if not isinstance(asset_url_parsed, EHentaiImageUrl):
            raise UnknownUrlError(asset_url_parsed)
        return asset_url_parsed


class EHentaiGalleryUrl(EHentaiUrl, GalleryUrl[EHentaiPageUrl]):
    patterns = {GALLERY_PATTERN: "https://{subdomain}.org/g/{gallery_id}/{gallery_token}"}

    def extract_posts(self) -> None:
        self.session.browser_login()
        self.session.browser.get(self.normalized_url)

        page_urls, thumb_urls = self._collect_page_urls()
        download_url = self._get_download_url()

        files = self._download_and_extract_archive(download_url)

        pages_thumbs_and_files = zip(page_urls, thumb_urls, files)
        self.posts = []
        for page_url, thumb_url, file in pages_thumbs_and_files:
            thumb_url.files = [file]
            page_url.assets = [thumb_url]
            self.posts.append(page_url)

    def _collect_page_urls(self) -> tuple[list["EHentaiPageUrl"], list["EHentaiImageUrl"]]:
        browser = self.session.browser
        page_elements = browser.find_elements_by_css_selector(".gdtl > a > img")

        thumb_urls = [self.parse(element.get_attribute("src")) for element in page_elements]

        urls = [
            self.build(
                url_type=EHentaiPageUrl,
                subdomain=self.properties["subdomain"],
                page_token=thumb.properties["page_token"],
                gallery_id=self.properties["gallery_id"],
                page_number=thumb_urls.index(thumb) + 1,
            )
            for thumb in thumb_urls
        ]

        return urls, thumb_urls  # type: ignore

    def _get_download_url(self) -> str:
        browser = self.session.browser

        archive_button, = browser.find_elements_by_text("Archive Download")
        archive_url = archive_button.get_attribute("onclick").removeprefix("return popUp('").split("'")[0]
        browser.get(archive_url)

        dl_button = browser.find_elements_by_text("Click Here To Start Downloading")[0].get_attribute("href")
        return dl_button

    def _download_and_extract_archive(self, download_url: str) -> list[File]:
        headers = {"Referer": self.normalized_url}
        try:
            archive_file = self.session.download_file(download_url, headers=headers)
        except DownloadError as e:
            if e.status_code == 410:
                raise EHEntaiRateLimit(e.response) from e
            else:
                raise
        assert isinstance(archive_file, ArchiveFile)
        return archive_file.extracted_files
