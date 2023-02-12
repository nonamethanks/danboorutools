from datetime import datetime
from typing import TYPE_CHECKING

from danboorutools.exceptions import DownloadError, EHEntaiRateLimit, UnknownUrlError
from danboorutools.logical.sessions.ehentai import EHentaiSession
from danboorutools.models.file import ArchiveFile, File
from danboorutools.models.url import AssetUrl, GalleryUrl, PostUrl, Url
from danboorutools.util.misc import compile_url, memoize, settable_property
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


BASE_DOMAIN = compile_url(r"(?:g\.)?(?P<subdomain>e(?:-|x)hentai)\.org")
GALLERY_PATTERN = compile_url(BASE_DOMAIN, r"\/g\/(?P<gallery_id>\d+)\/(?P<gallery_token>\w+)(?:\/.*)?")
PAGE_PATTERN = compile_url(BASE_DOMAIN, r"\/s\/(?P<page_token>\w+)\/(?P<gallery_id>\d+)-(?P<page_number>\d+)")
THUMBNAIL_PATTERN = compile_url(r"ehgt\.org\/\w{2}\/\w{2}\/(?P<page_token>\w{10})[\w-]+\.\w+")
PAGE_DOWNLOAD_PATTERN = compile_url(BASE_DOMAIN, r"\/fullimg\.php\?gid=(?P<gallery_id>\d+)&page=(?P<page_number>\d+)&key=\w+")
IMAGE_DIRECT_PATTERN = compile_url(
    r".*\.hath\.network:\d+\/h\/[\w-]+\/keystamp=[\w-]+;fileindex=\d+;xres=(?P<sample_size>\d+)\/(?P<filename>\w+)\.\w+"
)


class EHentaiUrl(Url):  # pylint: disable=abstract-method
    session = EHentaiSession()
    domains = ["e-hentai.org", "exhentai.org", "ehgt.org", "hath.network"]

    @property
    def html(self) -> "BeautifulSoup":
        if "This gallery has been removed or is unavailable" in super().html.text:
            self.normalized_url = self.normalized_url.replace("e-hentai.org", "exhentai.org")
            del self.__dict__["html"]
        return super().html


class EHentaiImageUrl(AssetUrl, EHentaiUrl):
    patterns = {
        THUMBNAIL_PATTERN: None,
        PAGE_DOWNLOAD_PATTERN: None,
        IMAGE_DIRECT_PATTERN: None,
    }

    @settable_property
    def created_at(self) -> datetime:
        return self.post.created_at

    @settable_property
    def is_deleted(self) -> bool:
        return self.post.is_deleted

    @settable_property
    def post(self) -> "EHentaiPageUrl":  # type: ignore[override]
        if post := getattr(self, "_post"):
            return post
        else:
            raise NotImplementedError


class EHentaiPageUrl(PostUrl, EHentaiUrl):
    patterns = {PAGE_PATTERN: "https://{subdomain}.org/s/{page_token}/{gallery_id}-{page_number}"}

    @settable_property
    def gallery(self) -> "EHentaiGalleryUrl":  # type: ignore[override]
        gallery_token = self.session.get_gallery_token_from_page_data(**self.url_properties)
        return self.build(url_type=EHentaiGalleryUrl,
                          gallery_token=gallery_token,
                          gallery_id=self.url_properties["gallery_id"],
                          subdomain=self.url_properties["subdomain"])

    @settable_property
    def assets(self) -> list[EHentaiImageUrl]:  # type: ignore[override]
        asset = self._get_direct_url()

        asset.post = self
        asset.created_at = self.created_at
        asset.files = asset.files

        return [asset]

    def _get_direct_url(self) -> EHentaiImageUrl:
        # Can't be cached because download urls expire fast
        # unlike in the Gallery, here not even the first page fetch itself can be cached because the link extraction is time-dependant
        get_original_el = self.html.select_one(':-soup-contains-own("Download original")')
        if get_original_el:
            asset_url = get_original_el["href"]
        else:
            get_original_el, = self.html.select("img#img")
            asset_url = get_original_el["src"]

        asset_url_parsed = self.parse(asset_url)
        if not isinstance(asset_url_parsed, EHentaiImageUrl):
            raise UnknownUrlError(asset_url_parsed)
        return asset_url_parsed

    @settable_property
    def created_at(self) -> datetime:
        return self.gallery.created_at

    @settable_property
    def is_deleted(self) -> bool:
        return self.gallery.is_deleted

    @settable_property
    def score(self) -> int:
        return self.gallery.score


class EHentaiGalleryUrl(GalleryUrl, EHentaiUrl):
    patterns = {GALLERY_PATTERN: "https://{subdomain}.org/g/{gallery_id}/{gallery_token}"}

    @settable_property
    def posts(self) -> list[EHentaiPageUrl]:  # type: ignore[override]
        raw_thumb_urls = self._get_thumb_urls()

        download_url = self._get_download_url()
        files = self._download_and_extract_archive(download_url)

        pages: list[EHentaiPageUrl] = []
        for raw_thumb_url, file in zip(raw_thumb_urls, files):
            image: EHentaiImageUrl = self.parse(raw_thumb_url)  # type: ignore[assignment]

            page = self.build(
                url_type=EHentaiPageUrl,
                subdomain=self.url_properties["subdomain"],
                page_token=image.url_properties["page_token"],
                gallery_id=self.url_properties["gallery_id"],
                page_number=raw_thumb_urls.index(raw_thumb_url) + 1,
            )

            image.post = page
            image.created_at = self.created_at
            image.files = [file]

            page.gallery = self
            page.assets = [image]
            page.created_at = self.created_at
            page.score = self.score

            pages.append(page)
        return pages

    @settable_property
    def created_at(self) -> datetime:
        element, = self.html.select('#gmid .gdt1:-soup-contains-own("Posted:")')
        datetime_element, = element.parent.select(".gdt2")
        return datetime_from_string(datetime_element.text)

    @settable_property
    def score(self) -> int:
        element, = self.html.select('#gmid .gdt1:-soup-contains-own("Favorited:")')
        score_element, = element.parent.select(".gdt2")
        return int(score_element.text.split()[0])

    @settable_property
    def is_deleted(self) -> bool:
        return bool(not self.html.select(".ptt td"))

    @memoize
    def _get_thumb_urls(self) -> list[str]:
        gallery_paginator = self.html.select(".ptt td")
        if len(gallery_paginator) > 3:
            raise NotImplementedError("Gallery paginator not implemented.")

        page_elements = self.html.select(".gdtl > a > img")

        thumb_urls = [element["src"] for element in page_elements]
        return thumb_urls

    def _get_download_url(self) -> str:
        # Can't be cached because download urls expire fast
        archive_button, = self.html.select(':-soup-contains-own("Archive Download")')
        archive_url = archive_button["onclick"].removeprefix("return popUp('").split("'")[0]

        browser = self.session.browser
        browser.get(archive_url)
        download_url = browser.find_elements_by_text("Click Here To Start Downloading")[0].get_attribute("href")
        return download_url

    @memoize
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
