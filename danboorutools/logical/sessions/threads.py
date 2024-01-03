from __future__ import annotations

import re

from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.instagram import InstagramArtistUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class ThreadsSession(Session):

    def artist_data(self, username: str) -> ThreadsArtistData:
        first_request = self.get(f"https://www.threads.net/@{username}")

        csrf_token = re.search(r'csrf_token":"([\w-]+)"', first_request.text)
        lsd_token = re.search(r'LSD",\[\],{"token":"(.*?)"},', first_request.text)

        assert csrf_token and lsd_token, (csrf_token, lsd_token)

        cookies = {
            "csrftoken": csrf_token.groups()[0],
        }

        data = {
            "lsd": lsd_token.groups()[0],
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "BarcelonaUsernameHoverCardImplQuery",
            "variables": f'{{"username":"{username}"}}',
            "doc_id": "6294229744032325",
        }

        headers = {
            "Referer": "https://www.threads.net/@mawari5577",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-FB-Friendly-Name": "BarcelonaUsernameHoverCardImplQuery",
            "X-IG-App-ID": "238260118697367",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        response = self.post("https://www.threads.net/api/graphql", cookies=cookies, headers=headers, data=data)

        return ThreadsArtistData(**response.json()["data"]["xdt_user_by_username"])


class ThreadsArtistData(BaseModel):
    username: str
    full_name: str

    biography: str

    @property
    def related_urls(self) -> list[Url]:
        return [InstagramArtistUrl.build(username=self.username)]
        # too much work to extract other stuff. Fuck this gay site
