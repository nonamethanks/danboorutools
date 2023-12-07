import re

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import vk
from danboorutools.models.url import UnsupportedUrl, Url

username_pattern = re.compile(r"^(?:public(?P<user_id>\d+))|(?P<username>[\w\.]+)$")
post_pattern = re.compile(r"^wall-?(?P<user_id>\d+)(?:_(?P<post_id>\d+)(?:_\w+)?)?")
photo_pattern = re.compile(r"^photo-?(?P<user_id>\d+)(?:_(?P<photo_id>\d+))?$")
album_pattern = re.compile(r"^album-?(?P<user_id>\d+)(?:_(?P<album_id>\d+))$")
file_pattern = re.compile(r"^doc-?(?P<user_id>\d+)(?:_(?P<file_id>\d+))$")


class VkComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # https://vk.com/topic-115903485_33484044?post=2
            case path, if path.startswith("topic-"):
                return UnsupportedUrl(parsed_url=parsable_url)

            case path, :
                url_type: type[Url]
                properties: dict[str, str] = {}
                for subpath in [path, *parsable_url.query.get("z", "").split("/"), *parsable_url.query.get("w", "").split("/")]:
                    for pattern in [username_pattern, post_pattern, photo_pattern, album_pattern, file_pattern]:
                        if match := pattern.match(subpath):
                            properties |= match.groupdict()

                if parsable_url.query.get("reply"):
                    properties["reply_id"] = parsable_url.query["reply"]

                if properties.get("reply_id"):
                    url_type = vk.VkPostReplyUrl
                elif properties.get("post_id"):
                    url_type = vk.VkPostUrl
                elif properties.get("photo_id"):
                    url_type = vk.VkPhotoUrl
                elif properties.get("file_id"):
                    url_type = vk.VkFileUrl
                elif properties.get("album_id"):
                    url_type = vk.VkAlbumUrl
                elif properties.get("username"):
                    url_type = vk.VkArtistUrl
                elif properties.get("user_id"):
                    url_type = vk.VkArtistIdUrl
                else:
                    raise NotImplementedError(parsable_url.raw_url, properties)

                return url_type(parsed_url=parsable_url, **properties)

            # https://vk.com/amaksart/rocjoker0120
            case path, _tag if username_pattern.match(path):
                return vk.VkArtistUrl(parsed_url=parsable_url,
                                      username=path)

            case _:
                return None
