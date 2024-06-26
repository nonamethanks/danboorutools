from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Literal

import ring

from danboorutools.exceptions import DeadUrlError, DownloadError, EHEntaiRateLimitError, UnknownUrlError
from danboorutools.logical.sessions.ehentai import EHentaiSession
from danboorutools.models.file import ArchiveFile, File
from danboorutools.models.url import GalleryUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from datetime import datetime

    from bs4 import BeautifulSoup


class EHentaiUrl(Url):
    session = EHentaiSession()

    site_name = "e-hentai"

    @cached_property
    def html(self) -> BeautifulSoup:
        if not isinstance(self, EHentaiPageUrl | EHentaiGalleryUrl):
            raise TypeError
        self.session.browser_login()
        try:
            self.session.head(self.normalized_url)
        except DeadUrlError:
            if self.subsite == "exhentai":  # pylint: disable=access-member-before-definition
                raise
            else:
                self.subsite = "exhentai"  # pylint: disable=attribute-defined-outside-init
                del self.__dict__["normalized_url"]
                return self.html

        browser = self.session.browser

        if browser.current_url != self.normalized_url:
            browser.get(self.normalized_url)

        return BeautifulSoup(browser.page_source, "html5lib")


class EHentaiImageUrl(PostAssetUrl, EHentaiUrl):
    image_type: Literal["direct", "thumbnail", "download", "hash_link"]  # TODO: fix the rest of possible url types in other extractors
    original_filename: str | None
    file_hash: str | None  # TODO: use this to find the original gallery, maybe combined with original filename?
    gallery_id: int | None = None
    page_number: int | None = None
    page_token: str | None = None  # TODO: is this just file_hash[:10] every time? i don't think so

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

    normalize_template = "https://{subsite}.org/s/{page_token}/{gallery_id}-{page_number}"

    @cached_property
    def gallery(self) -> EHentaiGalleryUrl:
        gallery_token = self.session.get_gallery_token_from_page_data(gallery_id=self.gallery_id,
                                                                      page_token=self.page_token,
                                                                      page_number=self.page_number)
        return EHentaiGalleryUrl.build(gallery_token=gallery_token,
                                       gallery_id=self.gallery_id,
                                       subsite=self.subsite)

    def _extract_assets(self) -> list[EHentaiImageUrl]:
        asset = self._get_direct_url()
        asset.extract_files()
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

        asset_url_parsed = EHentaiImageUrl.parse_and_assert(asset_url)
        return asset_url_parsed

    @cached_property
    def created_at(self) -> datetime:
        return self.gallery.created_at

    @cached_property
    def score(self) -> int:
        return self.gallery.score


class EHentaiGalleryUrl(GalleryUrl, EHentaiUrl):
    gallery_id: int
    gallery_token: str
    subsite: str

    normalize_template = "https://{subsite}.org/g/{gallery_id}/{gallery_token}"

    def _extract_posts_from_each_page(self) -> None:
        raise NotImplementedError("Rewrite me")
        if self.known_posts:
            return

        raw_thumb_urls = self._get_thumb_urls()

        download_url = self._get_download_url()
        files = self._download_and_extract_archive(download_url)

        for raw_thumb_url, file in zip(raw_thumb_urls, files, strict=True):
            image: EHentaiImageUrl = self.parse(raw_thumb_url)  # type: ignore[assignment]
            assert image.page_token
            image.files = [file]

            page = EHentaiPageUrl.build(
                subsite=self.subsite,
                page_token=image.page_token,
                gallery_id=self.gallery_id,
                page_number=raw_thumb_urls.index(raw_thumb_url) + 1,
            )

            self._register_post(
                post=page,
                assets=[image],
                created_at=self.created_at,
                score=self.score,
            )

    @cached_property
    def created_at(self) -> datetime:
        element, = self.html.select('#gmid .gdt1:-soup-contains-own("Posted:")')
        datetime_element, = element.parent.select(".gdt2")
        return datetime_from_string(datetime_element.text)

    @cached_property
    def score(self) -> int:
        element, = self.html.select('#gmid .gdt1:-soup-contains-own("Favorited:")')
        score_element, = element.parent.select(".gdt2")
        return int(score_element.text.split()[0])

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

    @ring.lru()
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
