from __future__ import annotations

from functools import cached_property

from danboorutools.models.url import ArtistUrl, PostUrl, RedirectUrl, Url


class VkUrl(Url):
    ...


class VkArtistUrl(ArtistUrl, VkUrl):
    username: str
    user_id: str | None = None

    normalize_template = "https://vk.com/{username}"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one(".page_name"))
        return [name_el.text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []  # those results are not reliable

    @property
    def vk_id_url(self) -> VkArtistIdUrl:
        if self.user_id:
            return VkArtistIdUrl.build(user_id=self.user_id)
        assert (url_el := self.html.select_one("meta[property='og:url']"))
        assert isinstance(user_id_url := Url.parse(url_el["content"]), VkArtistIdUrl)
        return user_id_url


class VkArtistIdUrl(RedirectUrl, VkUrl):
    user_id: str

    normalize_template = "https://vk.com/public{user_id}"

    @cached_property
    def resolved(self) -> VkArtistUrl:
        assert (mobile_link_el := self.html.select_one("link[rel='alternate'][media='only screen and (max-width: 640px)']"))
        url = Url.parse(mobile_link_el["href"])
        assert isinstance(url, VkArtistUrl)
        return url


class VkPostUrl(PostUrl, VkUrl):
    post_id: str
    user_id: str

    photo_id: str | None = None
    album_id: str | None = None
    username: str | None = None

    normalize_template = "https://vk.com/wall-{user_id}_{post_id}"


class VkPostReplyUrl(PostUrl, VkUrl):
    reply_id: str
    user_id: str
    post_id: str

    photo_id: str | None = None
    album_id: str | None = None
    username: str | None = None

    normalize_template = "https://vk.com/wall-{user_id}_{post_id}?reply={reply_id}"


class VkPhotoUrl(PostUrl, VkUrl):
    user_id: str
    photo_id: str

    album_id: str | None = None
    username: str | None = None

    normalize_template = "https://vk.com/photo-{user_id}_{photo_id}"


class VkFileUrl(PostUrl, VkUrl):
    file_id: str
    user_id: str

    album_id: str | None = None
    username: str | None = None

    normalize_template = "https://vk.com/doc{user_id}_{file_id}"


class VkAlbumUrl(PostUrl, VkUrl):
    user_id: str
    album_id: str

    username: str | None = None

    normalize_template = "https://vk.com/album-{user_id}_{album_id}"
