from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import artstation as a

RESERVED_USERNAMES = ["about", "blogs", "challenges", "guides", "jobs", "learning",
                      "marketplace", "prints", "schools", "search", "studios"]


class ArtstationComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> a.ArtStationUrl | None:
        if parsable_url.subdomain in ["", "www"]:
            return cls._match_username_in_path(parsable_url)
        elif parsable_url.subdomain.startswith("cdn"):
            return cls._match_image(parsable_url)
        else:
            return cls._match_username_in_subdomain(parsable_url)

    @staticmethod
    def _match_username_in_path(parsable_url: ParsableUrl) -> a.ArtStationUrl | None:
        match parsable_url.url_parts:
            # https://www.artstation.com/artwork/04XA4
            # https://www.artstation.com/artwork/cody-from-sf # (old; redirects to https://www.artstation.com/artwork/3JJA)
            case "artwork", *rest:
                if not rest:
                    return None

                post_title_or_id = rest[0]
                if "-" in post_title_or_id:
                    return a.ArtStationOldPostUrl(parsed_url=parsable_url,
                                                  post_title=post_title_or_id)
                else:
                    return a.ArtStationPostUrl(parsed_url=parsable_url,
                                               post_id=post_title_or_id,
                                               username=None)

            # https://artstation.com/artist/sa-dui
            # https://www.artstation.com/artist/chicle/albums/all/
            # https://www.artstation.com/artist/sa-dui
            case "artist", username, *_:
                return a.ArtStationArtistUrl(parsed_url=parsable_url,
                                             username=username)

            # https://www.artstation.com/marketplace/p/X9P5
            case "marketplace", "p", post_id:
                return a.ArtStationMarketplacePostUrl(parsed_url=parsable_url,
                                                      post_id=post_id)

            # http://www.artstation.com/envie_dai/prints
            # https://www.artstation.com/chicle/albums/all
            # https://www.artstation.com/felipecartin/profile
            # https://www.artstation.com/h-battousai/albums/1480261
            # https://www.artstation.com/sa-dui
            case username, *_:
                return a.ArtStationArtistUrl(parsed_url=parsable_url,
                                             username=username)

            case _:
                return None

    @staticmethod
    def _match_image(parsable_url: ParsableUrl) -> a.ArtStationUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://cdna.artstation.com/p/assets/images/images/005/804/224/large/titapa-khemakavat-sa-dui-srevere.jpg?1493887236
            # https://cdnb.artstation.com/p/assets/images/images/014/410/217/smaller_square/bart-osz-bartosz1812041.jpg?1543866276
            # https://cdna.artstation.com/p/assets/images/images/007/253/680/4k/ina-wong-demon-girl-done-ttd-comp.jpg?1504793833
            # https://cdna.artstation.com/p/assets/covers/images/007/262/828/small/monica-kyrie-1.jpg?1504865060
            case "p", "assets", ("images" | "covers") as asset_type, "images", *subdirs, _size, filename:
                return a.ArtStationImageUrl(parsed_url=parsable_url,
                                            filename=filename,
                                            asset_type=asset_type,
                                            asset_subdirs="/".join(subdirs))

            # https://cdn-animation.artstation.com/p/video_sources/000/466/622/workout.mp4
            case "p", "video_sources", *subdirs, filename if parsable_url.hostname == "cdn-animation.artstation.com":
                return a.ArtStationImageUrl(parsed_url=parsable_url,
                                            filename=filename,
                                            asset_type="video_sources",
                                            asset_subdirs="/".join(subdirs))

            case _:
                return None

    @staticmethod
    def _match_username_in_subdomain(parsable_url: ParsableUrl) -> a.ArtStationUrl | None:
        match parsable_url.url_parts:
            # https://sa-dui.artstation.com/projects/DVERn
            # https://dudeunderscore.artstation.com/projects/NoNmD?album_id=23041
            case "projects", post_id:
                return a.ArtStationPostUrl(parsed_url=parsable_url,
                                           post_id=post_id,
                                           username=parsable_url.subdomain)

            # https://heyjay.artstation.com/store/art_posters
            # https://hosi_na.artstation.com
            # https://sa-dui.artstation.com
            # https://sa-dui.artstation.com/projects
            case _:
                return a.ArtStationArtistUrl(parsed_url=parsable_url,
                                             username=parsable_url.subdomain)
