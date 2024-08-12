from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING, Literal

import ring
from bs4 import BeautifulSoup

from danboorutools.exceptions import DeadUrlError, NotAnArtistError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url, parse_list
from danboorutools.util.misc import BaseModel, extract_urls_from_string

if TYPE_CHECKING:
    from danboorutools.logical.urls.patreon import PatreonGalleryImageUrl


class PatreonSession(Session):
    @property
    def cookies_from_env(self) -> dict:
        return {"session_id": os.environ["PATREON_SESSION_ID_COOKIE"]}

    @ring.lru()
    def artist_data(self, url: str) -> PatreonArtistData:
        response = self.get(url, cookies=self.cookies_from_env)
        parsed_data = response.search_json(
            pattern=r"({\"props\".*})",
            selector="script#__NEXT_DATA__",
        )

        user_data = parsed_data["props"]["pageProps"]["bootstrapEnvelope"]["pageBootstrap"]
        csrf = parsed_data["props"]["pageProps"]["bootstrapEnvelope"]["csrfSignature"]

        try:
            return PatreonArtistData(**user_data["campaign"], csrf_token=csrf)
        except KeyError as e:
            if user_data.get("pageUser"):
                if user_data["pageUser"]["data"]["type"] == "user":
                    raise NotAnArtistError(url) from e
                else:
                    raise NotImplementedError(user_data) from e
            if user_data["curtainType"] == "user_removed":
                raise DeadUrlError(response) from e

            e.add_note(f"User data: {user_data}")
            raise
        except TypeError as e:
            if user_data["curtainType"] == "campaign_removed":
                raise DeadUrlError(response) from e

            e.add_note(f"User data: {user_data}")
            raise

    def subscribe(self, artist_url: str) -> None:
        artist_data = self.artist_data(artist_url)
        if artist_data.data.attributes.current_user_is_free_member:
            return

        headers = {
            "Referer": artist_url,
            "Content-Type": "application/vnd.api+json",
            "x-csrf-signature": artist_data.csrf_token,
        }

        data_json = {
            "data": {
                "type": "free-membership-subscription",
                "attributes": {},
                "relationships": {
                        "campaign": {
                            "data": {
                                "type": "campaign",
                                "id": artist_data.data.id,
                            },
                        },
                },
            },
        }

        url = (
            "https://www.patreon.com/api/free-membership-subscription"
            "?include=campaign,reward.null"
            "&fields[free-membership-subscription]=started_at,ended_at"
            "&fields[campaign]=avatar_photo_url,cover_photo_url,name,pay_per_name,pledge_url,published_at,url"
            "&fields[patron]=image_url,full_name,url"
            "&fields[reward]=amount_cents,description,is_free_tier,requires_shipping,title,unpublished_at"
            "&json-api-version=1.0&json-api-use-default-includes=false"
        )

        response = self.post(
            url=url,
            cookies=self.cookies_from_env,
            headers=headers,
            data=json.dumps(data_json, separators=(",", ":")),
        )
        try:
            data = response.json()["data"]
            assert data["attributes"]["started_at"]
            assert data["type"] == "free-membership-subscription"
        except Exception as e:
            raise NotImplementedError(str(response.json())) from e

    def get_feed(self, cursor: str | None) -> PatreonCampaignResponse:
        headers = {
            "Referer": "https://www.patreon.com/home",
            "Content-Type": "application/vnd.api+json",
        }

        data_url = self._generate_data_url(campaign="feed", cursor=cursor)
        data = self.get(data_url, headers=headers, cookies=self.cookies_from_env).json()

        return PatreonCampaignResponse(**data)

    def get_posts(self, campaign_id: int, cursor: str | None) -> PatreonCampaignResponse:
        headers = {
            "Referer": "https://www.patreon.com/home",
            "Content-Type": "application/vnd.api+json",
        }

        data_url = self._generate_data_url(campaign=campaign_id, cursor=cursor)
        data = self.get(data_url, headers=headers).json()  # , cookies=self.cookies_from_env).json()

        return PatreonCampaignResponse(**data)

    def _generate_data_url(self, campaign: int | Literal["feed"], cursor: str | None = None) -> str:
        _type = "stream" if campaign == "feed" else "posts"

        url = (
            f"https://www.patreon.com/api/{_type}"

            "?include=user,images,attachments,user_defined_tags,campaign,poll.choices,"
            "poll.current_user_responses.user,poll.current_user_responses.choice,media,"
            "poll.current_user_responses.poll,access_rules.tier.null,audio,audio_preview.null"

            "&fields[post]=change_visibility_at,comment_count,commenter_count,content,current_user_can_delete,"
            "current_user_can_comment,current_user_can_view,current_user_has_liked,embed,"
            "image,is_paid,like_count,min_cents_pledged_to_view,post_file,published_at,"
            "patron_count,patreon_url,post_type,pledge_url,thumbnail_url,"
            "teaser_text,title,upgrade_url,url,was_posted_by_campaign_owner"
            "&fields[user]=image_url,full_name,url"
            "&fields[campaign]=avatar_photo_url,earnings_visibility,is_nsfw,is_monthly,name,url"
            "&fields[access_rule]=access_rule_type,amount_cents"
            "&fields[post_tag]=tag_type,value"
            "&fields[media]=id,image_urls,download_url,metadata,file_name"

            "&sort=-published_at"
            "&filter[is_draft]=false"
            "&filter[contains_exclusive_posts]=true"

            "&json-api-version=1.0"
            "&json-api-use-default-includes=false"
        )

        url += "&filter[is_following]=true" if campaign == "feed" else f"&filter[campaign_id]={campaign}"

        if cursor:
            url += f"&page[cursor]={cursor}"
        return url


class PatreonArtistAttributes(BaseModel):
    cover_photo_url_sizes: dict[str, str]

    current_user_is_free_member: bool

    summary: str
    name: str
    vanity: str | None
    url: str


class _ArtistData(BaseModel):
    attributes: PatreonArtistAttributes
    id: int


class PatreonArtistData(BaseModel):
    included: list[dict]
    data: _ArtistData
    csrf_token: str

    @property
    def name(self) -> str:
        return self.data.attributes.name

    @property
    def username(self) -> str | None:
        return self.data.attributes.vanity

    @property
    def artist_url(self) -> str:
        return self.data.attributes.url

    @property
    def related_urls(self) -> list[Url]:
        urls = extract_urls_from_string(self.data.attributes.summary)
        useless_subtypes = ("user", "post_aggregation", "goal", "free_trial_configuration",
                            "access-rule", "free-membership-subscription")

        for included in self.included:
            if included["type"].startswith("reward"):
                continue
            if included["type"] in useless_subtypes:
                continue
            if included["type"] == "social-connection":
                url_string = included["attributes"]["external_profile_url"]
                if not url_string:
                    if included["attributes"]["app_name"] == "twitter":
                        continue  # for some reason patreon still includes this
                    elif included["attributes"]["app_name"] == "facebook":
                        if not included["attributes"]["display_name"] and not included["attributes"]["external_profile_url"]:
                            continue
                        raise NotImplementedError(included)
                    else:
                        raise NotImplementedError(included)
                urls += [url_string]
                continue
            raise NotImplementedError(included)

        return parse_list(urls, Url)

    @property
    def reward_images(self) -> list[PatreonGalleryImageUrl]:
        urls = [
            image_url
            for i in self.included if i["type"] == "reward"
            if (image_url := i["attributes"].get("image_url"))
        ]
        from danboorutools.logical.urls.patreon import PatreonGalleryImageUrl
        return parse_list(urls, PatreonGalleryImageUrl)


class PatreonCampaignPostDataAttrs(BaseModel):
    current_user_can_view: bool
    content: str | None = None
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
