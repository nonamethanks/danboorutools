from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class VgenSession(Session):
    def artist_data(self, username: str) -> VgenArtistData:
        artist_data = self.get(f"https://vgen.co/{username}").search_json(pattern=r"(.*)", selector="#__NEXT_DATA__")
        return VgenArtistData(**artist_data["props"]["pageProps"]["user"])


class VgenArtistData(BaseModel):
    displayName: str

    socials: list[dict[str, str]]
    contactSocials: dict[str, str]

    bio: str

    @property
    def related_urls(self) -> list[Url]:
        urls = [Url.parse(social["link"]) for social in self.socials]
        if any(self.contactSocials.values()):
            raise NotImplementedError(self.contactSocials)

        urls += list(map(Url.parse, extract_urls_from_string(self.bio)))
        return urls
