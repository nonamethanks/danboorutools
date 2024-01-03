from __future__ import annotations

import os
from datetime import datetime
from typing import Literal

import ring
from bs4 import BeautifulSoup

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string

# JSON_DATA_PATTERN = re.compile(r"bootstrap, ({.*?)\);\s", re.DOTALL)


class PatreonSession(Session):
    @ring.lru()
    def artist_data(self, url: str) -> PatreonArtistData:
        response = self.get(url)
        parsed_data = response.search_json(
            pattern=r"({\"props\".*})",
            selector="script#__NEXT_DATA__",
        )

        user_data = parsed_data["props"]["pageProps"]["bootstrapEnvelope"]["bootstrap"]

        try:
            return PatreonArtistData(**user_data["campaign"])
        except KeyError as e:
            if user_data["curtainType"] == "user_removed":
                raise DeadUrlError(response) from e
            raise NotImplementedError(user_data) from e

    @property
    def cookies_from_env(self) -> dict:
        return {"session_id": os.environ["PATREON_SESSION_ID_COOKIE"]}

    def get_feed(self, cursor: str | None) -> PatreonCampaignResponse:
        headers = {
            "Referer": "https://www.patreon.com/home",
            "Content-Type": "application/vnd.api+json",
        }

        data_url = self._generate_data_url(campaign="feed", cursor=cursor)
        data = self.get(data_url, headers=headers, cookies=self.cookies_from_env).json()

        return PatreonCampaignResponse(**data)

    def _generate_data_url(self, campaign: int | Literal["feed"], cursor: str | None = None) -> str:
        _type = "stream" if campaign == "feed" else "posts"

        url = (
            f"https://www.patreon.com/api/{_type}"

            "?include=user,images,attachments,user_defined_tags,campaign,poll.choices,"
            "poll.current_user_responses.user,poll.current_user_responses.choice,"
            "poll.current_user_responses.poll,access_rules.tier.null"

            "&fields[post]=change_visibility_at,comment_count,content,current_user_can_delete,"
            "current_user_can_view,current_user_has_liked,embed,"
            "image,is_paid,like_count,min_cents_pledged_to_view,post_file,published_at,"
            "patron_count,patreon_url,post_type,pledge_url,thumbnail_url,"
            "teaser_text,title,upgrade_url,url,was_posted_by_campaign_owner"
            "&fields[user]=image_url,full_name,url"
            "&fields[campaign]=avatar_photo_url,earnings_visibility,is_nsfw,is_monthly,name,url"
            "&fields[access_rule]=access_rule_type,amount_cents"
            "&sort=-published_at"
            "&filter[is_draft]=false"
            "&filter[contains_exclusive_posts]=true"

            "&json-api-use-default-includes=false"
            "&json-api-version=1.0"
        )

        url += "&filter[is_following]=true" if campaign == "feed" else f"&filter[campaign_id]={campaign}"

        if cursor:
            url += f"&page[cursor]={cursor}"
        return url


class PatreonArtistData(BaseModel):
    included: list[dict]
    data: dict

    @property
    def name(self) -> str:
        return self.data["attributes"]["name"]

    @property
    def username(self) -> str:
        return self.data["attributes"]["vanity"]

    @property
    def related_urls(self) -> list[Url]:
        urls = extract_urls_from_string(self.data["attributes"]["summary"])

        for included in self.included:
            if included["type"].startswith("reward"):
                continue
            if included["type"] in ("user", "post_aggregation", "goal", "free_trial_configuration"):
                continue
            if included["type"] == "social-connection":
                url_string = included["attributes"]["external_profile_url"]
                if not url_string:
                    if included["attributes"]["app_name"] == "twitter":
                        continue  # for some reason patreon still includes this
                    else:
                        raise NotImplementedError(included)
                urls += [url_string]
                continue
            raise NotImplementedError(included)

        return [Url.parse(u) for u in urls]


class PatreonCampaignPostDataAttrs(BaseModel):
    current_user_can_view: bool
    content: str | None
    patreon_url: str
    published_at: datetime
    like_count: int
    upgrade_url: str


class PatreonCampaignPostData(BaseModel):
    attributes: PatreonCampaignPostDataAttrs
    relationships: dict

    def get_assets(self, included: list[dict]) -> list[str]:
        entity_names = ["attachments", "images", "media"]
        entities = [entity for entity_name in entity_names
                    for entity in self.relationships.get(entity_name, {}).get("data", [])]

        assets = []
        for entity in entities:
            entity_data, = (included_json for included_json in included
                            if included_json["id"].isnumeric()
                            and int(entity["id"]) == int(included_json["id"]))

            attribute = entity_data["attributes"]
            if "image_urls" in attribute:
                assets.append(attribute["image_urls"]["original"])
            elif "url" in attribute:
                assets.append(attribute["url"])
            else:
                raise NotImplementedError(entity_data)

        if self.attributes.content:
            content_soup = BeautifulSoup(self.attributes.content, "html5lib")
            assets += [img["src"] for img in content_soup.select("img")]

        assets = [a for a in assets if "/media-u/" not in a]  # exclude video thumbs
        assets = list(dict.fromkeys(assets))
        return assets


class PatreonCampaignResponse(BaseModel):
    data: list[PatreonCampaignPostData]
    meta: dict
    included: list[dict]
