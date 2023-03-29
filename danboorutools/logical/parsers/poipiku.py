from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.poipiku import PoipikuArtistUrl, PoipikuImageUrl, PoipikuPostUrl, PoipikuUrl


class PoipikuComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PoipikuUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case _, user_id, _filename if parsable_url.subdomain in ["img-org", "img"]:

                file_stem_parts = parsable_url.stem.split("_")
                # https://img.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg_640.jpg
                # https://img-org.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg
                if len(file_stem_parts) == 3:
                    [post_id, _, image_hash] = file_stem_parts
                    image_id = int(file_stem_parts[1])  # I wish I could strangle typechecking coders over the internet

                # https://img.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg_640.jpg
                # https://img-org.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg
                elif len(file_stem_parts) == 2:
                    post_id, image_hash = file_stem_parts
                    image_id = None
                # https://img.poipiku.com/user_img02/000003310/000007036.jpeg_640.jpg
                # https://img-org.poipiku.com/user_img02/000003310/000007036.jpeg
                elif len(file_stem_parts) == 1:
                    post_id, = file_stem_parts
                    image_id = None
                    image_hash = None
                else:
                    raise ValueError(parsable_url.stem)

                return PoipikuImageUrl(parsed_url=parsable_url,
                                       post_id=int(post_id),
                                       image_id=image_id,
                                       image_hash=image_hash,
                                       user_id=int(user_id))

            # https://poipiku.com/6849873/8271386.html
            # https://poipiku.com/3310/7036.html
            # https://poipiku.com/20566/7204115.html
            # https://poipiku.com/20566/007185704.html
            case user_id, _filename if user_id.isnumeric():
                return PoipikuPostUrl(parsed_url=parsable_url,
                                      user_id=int(user_id),
                                      post_id=int(parsable_url.stem))

            # https://poipiku.com/IllustListPcV.jsp?ID=9056
            # https://poipiku.com/IllustListGridPcV.jsp?ID=9056
            case ("IllustListPcV.jsp" | "IllustListGridPcV.jsp" | "ActivityListPcV.jsp"), :
                return PoipikuArtistUrl(parsed_url=parsable_url,
                                        user_id=int(parsable_url.query["ID"]))

            # https://poipiku.com/6849873
            case user_id, if user_id.isnumeric():
                return PoipikuArtistUrl(parsed_url=parsable_url,
                                        user_id=int(user_id))

            case _:
                return None
