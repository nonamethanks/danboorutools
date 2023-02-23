from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Literal

from danboorutools.exceptions import DownloadError, EHEntaiRateLimitError, UnknownUrlError, UrlIsDeleted
from danboorutools.logical.sessions.ehentai import EHentaiSession
from danboorutools.models.file import ArchiveFile, File
from danboorutools.models.url import GalleryUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import memoize, settable_property
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class EHentaiUrl(Url):
    session = EHentaiSession()
    subsite: str | None = None

    @cached_property
    def html(self) -> BeautifulSoup:
        if not isinstance(self, (EHentaiPageUrl, EHentaiGalleryUrl)):
            raise ValueError

        try:
            return self.session.get_html(self.normalized_url)
        except UrlIsDeleted:
            if self.subsite == "exhentai":
                raise

        self.subsite = "exhentai"
        del self.__dict__["normalized_url"]
        return self.html


class EHentaiImageUrl(PostAssetUrl, EHentaiUrl):
    original_filename: str | None
    gallery_id: int | None = None
    page_number: int | None = None
    page_token: str | None = None  # TODO: is this just file_hash[:10] every time? i don't think so
    file_hash: str | None  # TODO: use this to find the original gallery, maybe combined with original filename?
    image_type: Literal["direct", "thumbnail", "download", "hash_link"]  # TODO: fix the rest of possible url types in other extractors

    @settable_property
    def created_at(self) -> datetime:
        return self.post.created_at

    @settable_property
    def post(self) -> EHentaiPageUrl:  # type: ignore[override]
        if post := getattr(self, "_post"):
            return post
        else:
            raise NotImplementedError

    @cached_property
    def full_size(self) -> str:
        if self.image_type == "download":
            return self.parsed_url.raw_url
        raise NotImplementedError(self.parsed_url)


class EHentaiPageUrl(PostUrl, EHentaiUrl):
    gallery_id: int
    page_number: int
    page_token: str
    subsite: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        subsite = kwargs["subsite"]
        page_token = kwargs["page_token"]
        gallery_id = kwargs["gallery_id"]
        page_number = kwargs["page_number"]
        return f"https://{subsite}.org/s/{page_token}/{gallery_id}-{page_number}"

    @settable_property
    def gallery(self) -> EHentaiGalleryUrl:  # type: ignore[override]
        gallery_token = self.session.get_gallery_token_from_page_data(gallery_id=self.gallery_id,
                                                                      page_token=self.page_token,
                                                                      page_number=self.page_number)
        return self.build(url_type=EHentaiGalleryUrl,
                          gallery_token=gallery_token,
                          gallery_id=self.gallery_id,
                          subsite=self.subsite)

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
    def score(self) -> int:
        return self.gallery.score


class EHentaiGalleryUrl(GalleryUrl, EHentaiUrl):
    gallery_id: int
    gallery_token: str
    subsite: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        subsite = kwargs["subsite"]
        gallery_id = kwargs["gallery_id"]
        gallery_token = kwargs["gallery_token"]
        return f"https://{subsite}.org/g/{gallery_id}/{gallery_token}"

    @settable_property
    def posts(self) -> list[EHentaiPageUrl]:  # type: ignore[override]
        raw_thumb_urls = self._get_thumb_urls()

        download_url = self._get_download_url()
        files = self._download_and_extract_archive(download_url)

        pages: list[EHentaiPageUrl] = []
        for raw_thumb_url, file in zip(raw_thumb_urls, files):
            image: EHentaiImageUrl = self.parse(raw_thumb_url)  # type: ignore[assignment]
            assert image.page_token
            page = self.build(
                url_type=EHentaiPageUrl,
                subsite=self.subsite,
                page_token=image.page_token,
                gallery_id=self.gallery_id,
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
                raise EHEntaiRateLimitError(e.response) from e
            else:
                raise
        assert isinstance(archive_file, ArchiveFile)
        return archive_file.extracted_files
