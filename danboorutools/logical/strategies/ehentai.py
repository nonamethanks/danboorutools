from danboorutools.exceptions import DownloadError, EHEntaiRateLimit
from danboorutools.logical.session import Session
from danboorutools.models.base_url import BaseAssetUrl, BaseGalleryUrl, BasePostUrl, BaseUrl
from danboorutools.models.file import ArchiveFile, File
from danboorutools.util import compile_url

BASE_DOMAIN = compile_url(r"(?:g\.)?(?P<subdomain>e(?:-|x)hentai)\.org")
GALLERY_PATTERN = compile_url(BASE_DOMAIN, r"\/g\/(?P<gallery_id>\d+)\/(?P<gallery_token>\w+)")
PAGE_PATTERN = compile_url(BASE_DOMAIN, r"\/s\/(?P<page_token>\w+)\/(?P<gallery_id>\d+)-(?P<page_number>\d+)")
THUMBNAIL_PATTERN = compile_url(r"ehgt\.org\/\w{2}\/\w{2}\/(?P<page_token>\w{10})[\w-]+\.\w+")


class EHentaiSession(Session):
    def _login(self) -> None:
        verification_url = "https://e-hentai.org/home.php"
        verification_element = ".homebox"

        if self.browser.attempt_login_with_cookies(domain=EHentaiUrl.site_name,
                                                   verification_url=verification_url,
                                                   verification_element=verification_element):
            return

        self.browser.compile_login_form(
            domain=EHentaiUrl.site_name,
            form_url="https://e-hentai.org/bounce_login.php",
            steps=[{
                "username": "[name='UserName']",
                "password": "[name='PassWord']",
                "submit": "[name='ipb_login_submit']",
            }],
            verification_url=verification_url,
            verification_element=verification_element,
        )


class EHentaiUrl(BaseUrl):
    site_name = "ehentai"
    session = EHentaiSession()
    domains = ["e-hentai.org", "exhentai.org", "ehgt.org"]


class EHentaiImageUrl(EHentaiUrl, BaseAssetUrl):
    patterns = {THUMBNAIL_PATTERN: None}


class EHentaiPageUrl(EHentaiUrl, BasePostUrl[EHentaiImageUrl]):
    assets: list["EHentaiImageUrl"]
    patterns = {PAGE_PATTERN: "https://{subdomain}.org/s/{page_token}/{gallery_id}-{page_number}"}


class EHentaiGalleryUrl(EHentaiUrl, BaseGalleryUrl[EHentaiPageUrl]):
    patterns = {GALLERY_PATTERN: "https://{subdomain}.org/g/{gallery_id}/{gallery_token}"}

    def extract_posts(self) -> None:
        self.session.login()
        self.session.browser.get(self.normalized_url)

        page_urls, thumb_urls = self.collect_page_urls()
        download_url = self.get_download_url()

        files = self.download_and_extract_archive(download_url)

        pages_thumbs_and_files = zip(page_urls, thumb_urls, files)
        self.posts = []
        for page_url, thumb_url, file in pages_thumbs_and_files:
            thumb_url.file = file
            page_url.assets = [thumb_url]
            self.posts.append(page_url)

    def collect_page_urls(self) -> tuple[list["EHentaiPageUrl"], list["EHentaiImageUrl"]]:
        browser = self.session.browser
        page_elements = browser.find_elements_by_css_selector(".gdtl > a > img")

        thumb_urls = [self.from_string(element.get_attribute("src")) for element in page_elements]

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

    def get_download_url(self) -> str:
        browser = self.session.browser

        archive_button, = browser.find_elements_by_text("Archive Download")
        archive_url = archive_button.get_attribute("onclick").removeprefix("return popUp('").split("'")[0]
        browser.get(archive_url)

        dl_button = browser.find_elements_by_text("Click Here To Start Downloading")[0].get_attribute("href")
        return dl_button

    def download_and_extract_archive(self, download_url: str) -> list[File]:
        cookies = {}
        for browser_cookie in self.session.browser.get_cookies():
            cookies[browser_cookie["name"]] = browser_cookie["value"]
        headers = {"Referer": self.normalized_url}
        try:
            archive_file = self.session.download_file(download_url, headers=headers, cookies=cookies)
        except DownloadError as e:
            if e.status_code == 410:
                raise EHEntaiRateLimit(e.response) from e
            else:
                raise
        assert isinstance(archive_file, ArchiveFile)
        return archive_file.extracted_files  # pylint: disable=no-member  # https://github.com/PyCQA/pylint/issues/4693
