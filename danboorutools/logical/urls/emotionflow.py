from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url
from danboorutools.util.misc import extract_urls_from_string

if TYPE_CHECKING:
    from bs4 import Tag


class EmotionflowUrl(Url):
    pass


class EmotionflowArtistUrl(ArtistUrl, EmotionflowUrl):
    user_id: int

    normalize_template = "https://galleria.emotionflow.com/{user_id}/"

    @property
    def primary_names(self) -> list[str]:
        name_el = self.profile_html.select_one(".CommonTitleUserName a[itemprop='name']")
        return [name_el.text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        about_section = self.profile_html.select_one(".Contents .ProfileList").text
        return [Url.parse(u) for u in extract_urls_from_string(about_section)]

    @cached_property
    def profile_html(self) -> Tag:
        return self.session.get(f"{self.normalized_url}profile.html").html


class EmotionflowPostUrl(PostUrl, EmotionflowUrl):
    post_id: int
    user_id: int

    normalize_template = "https://galleria.emotionflow.com/{user_id}/{post_id}.html"


class EmotionflowImageUrl(PostAssetUrl, EmotionflowUrl):
    user_id: int
    subdir: str

    @property
    def full_size(self) -> str:
        filename = re.sub(r"^(\w+\.\w+)_\d+\.\w+$", r"\1", self.parsed_url.filename)
        return f"https://galleria-img.emotionflow.com/{self.subdir}/{self.user_id}/{filename}"
