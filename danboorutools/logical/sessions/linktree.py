from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url, parse_list
from danboorutools.util.misc import BaseModel


class LinktreeSession(Session):
    def artist_data(self, username: str) -> LinktreeArtistData:
        data = self.get(f"https://linktr.ee/{username}").search_json(
            pattern=r"(.*)",
            selector="script#__NEXT_DATA__",
        )
        return LinktreeArtistData(**data["props"]["pageProps"]["account"])


class LinktreeArtistData(BaseModel):
    username: str

    socialLinks: list
    links: list

    @property
    def related(self) -> list[Url]:
        if self.socialLinks:
            raise NotImplementedError(self.socialLinks)

        return parse_list([link["url"] for link in self.links if link["url"]], Url)
