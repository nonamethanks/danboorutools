from danboorutools.logical.extractors.poipiku import PoipikuArtistUrl, PoipikuImageUrl, PoipikuPostUrl, PoipikuUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class PoipikuComParser(UrlParser):
    test_cases = {
        PoipikuArtistUrl: [
            "https://poipiku.com/IllustListPcV.jsp?ID=9056",
            "https://poipiku.com/IllustListGridPcV.jsp?ID=9056",
            "https://poipiku.com/6849873",
        ],
        PoipikuImageUrl: [
            "https://img.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg_640.jpg",
            "https://img-org.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg",
            "https://img.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg_640.jpg",
            "https://img-org.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg",
            "https://img.poipiku.com/user_img02/000003310/000007036.jpeg_640.jpg",
            "https://img-org.poipiku.com/user_img02/000003310/000007036.jpeg",
        ],
        PoipikuPostUrl: [
            "https://poipiku.com/6849873/8271386.html",
            "https://poipiku.com/3310/7036.html",
            "https://poipiku.com/20566/7204115.html",
            "https://poipiku.com/20566/007185704.html",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PoipikuUrl | None:
        instance: PoipikuUrl

        match parsable_url.url_parts:
            case _, user_id, _filename if parsable_url.subdomain in ["img-org", "img"]:
                instance = PoipikuImageUrl(parsable_url)
                instance.user_id = int(user_id)
                file_stem_parts = parsable_url.stem.split("_")
                if len(file_stem_parts) == 3:
                    [post_id, _, image_hash] = file_stem_parts
                    image_id = int(file_stem_parts[1])  # I wish I could strangle typechecking coders over the internet
                elif len(file_stem_parts) == 2:
                    post_id, image_hash = file_stem_parts
                    image_id = None
                elif len(file_stem_parts) == 1:
                    post_id, = file_stem_parts
                    image_id = None
                    image_hash = None
                else:
                    raise ValueError(parsable_url.stem)

                instance.post_id = int(post_id)
                instance.image_id = image_id
                instance.image_hash = image_hash

            case user_id, filename if user_id.isnumeric():
                instance = PoipikuPostUrl(parsable_url)
                instance.user_id = int(user_id)
                instance.post_id = int(parsable_url.stem)

            case ("IllustListPcV.jsp" | "IllustListGridPcV.jsp" | "ActivityListPcV.jsp"), :
                instance = PoipikuArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.params["ID"])

            case user_id, if user_id.isnumeric():
                instance = PoipikuArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case _:
                return None

        return instance
