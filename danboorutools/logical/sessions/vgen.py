from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.instagram import InstagramArtistUrl
from danboorutools.logical.urls.twitter import TwitterArtistUrl
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
        for site_name, handle in self.contactSocials.items():
            if not handle:
                continue

            if site_name == "discord":
                pass
            elif site_name == "twitter":
                urls += [TwitterArtistUrl.build(username=handle)]
            elif site_name == "instagram":
                urls += [InstagramArtistUrl.build(username=handle)]
            else:
                raise NotImplementedError(site_name, handle)

        urls += list(map(Url.parse, extract_urls_from_string(self.bio)))
        return list(set(urls))
