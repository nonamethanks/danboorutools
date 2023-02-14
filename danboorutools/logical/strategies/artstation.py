from danboorutools.models.url import ArtistUrl, AssetUrl, PostUrl, RedirectUrl
from danboorutools.util.misc import compile_url

REGEX_POST = compile_url(
    r"https?:\/\/(?:(?:www\.)?artstation\.com\/artwork|(?P<artist_name>[\w-]+)\.artstation\.com\/projects)\/(?P<post_id>(?!\w+-)[\w]+)"
)

REGEX_OLD_POST = compile_url(r"https?:\/\/(?:www\.)?artstation\.com\/artwork\/(?P<post_id>(?:[\w-])+-\w+)")

REGEX_IMAGE = compile_url(
    r"https?:\/\/cdn(?:-animation|\w)?\.artstation\.com\/p\/",
    r"(?:(?:assets\/(?:covers|images)\/images)|video_sources)\/(?:\d+\/){3}(?:(?P<image_size>\w+)\/)?",
    r"(?P<image_title>[\w-]+)\.(?P<image_extension>\w+)"
)

RESERVED_PATHS = ["about", "blogs", "challenges", "guides", "jobs", "learning",
                  "marketplace", "prints", "schools", "search", "studios", "artwork"]
_DOMAIN_WITH_ARTIST_NAME = r"(?P<artist_name>(?!www|cdn\w?)[\w-]+)\.artstation\.com"
REGEX_ARTIST = compile_url(
    r"https?:\/\/(?:",
    _DOMAIN_WITH_ARTIST_NAME + r"(?:\/(?:projects|(?:(?!projects).*))\/?)?$"
    r"|",
    r"(?:www\.)?artstation\.com\/(?:artist\/)?(?P<artist_name>(?!" + "|".join(RESERVED_PATHS) + r")[\w-]+)"
    r")",
)


class ArtStationPostUrl(PostUrl):
    test_cases = [
        "https://www.artstation.com/artwork/04XA4",
        "https://sa-dui.artstation.com/projects/DVERn",
        "https://dudeunderscore.artstation.com/projects/NoNmD?album_id=23041",
    ]
    domains = ["artstation.com"]
    pattern = REGEX_POST
    normalization = "https://{artist_name}.artstation.com/projects/{post_id}"
    id_name = "post_id"


class ArtStationOldPostUrl(RedirectUrl):
    test_cases = [
        "https://www.artstation.com/artwork/cody-from-sf",  # (old; redirects to https://www.artstation.com/artwork/3JJA)
    ]
    domains = ["artstation.com"]
    pattern = REGEX_OLD_POST
    id_name = "post_id"


class ArtStationArtistUrl(ArtistUrl):
    test_cases = [
        "http://artstation.com/sha_sha",
        "http://www.artstation.com/envie_dai/prints",
        "https://artstation.com/artist/sa-dui",
        "https://heyjay.artstation.com/store/art_posters",
        "https://hosi_na.artstation.com",
        "https://sa-dui.artstation.com",
        "https://sa-dui.artstation.com/projects",
        "https://www.artstation.com/artist/chicle/albums/all/",
        "https://www.artstation.com/artist/sa-dui",
        "https://www.artstation.com/chicle/albums/all",
        "https://www.artstation.com/felipecartin/profile",
        "https://www.artstation.com/h-battousai/albums/1480261",
        "https://www.artstation.com/sa-dui",
    ]
    domains = ["artstation.com"]
    pattern = REGEX_ARTIST
    normalization = "https://www.artstation.com/{artist_name}"
    id_name = "artist_name"


class ArtStationImageUrl(AssetUrl):
    test_cases = [
        "https://cdna.artstation.com/p/assets/images/images/005/804/224/large/titapa-khemakavat-sa-dui-srevere.jpg?1493887236",
        "https://cdnb.artstation.com/p/assets/images/images/014/410/217/smaller_square/bart-osz-bartosz1812041.jpg?1543866276",
        "https://cdna.artstation.com/p/assets/images/images/007/253/680/4k/ina-wong-demon-girl-done-ttd-comp.jpg?1504793833",
        "https://cdna.artstation.com/p/assets/covers/images/007/262/828/small/monica-kyrie-1.jpg?1504865060",
        "https://cdn-animation.artstation.com/p/video_sources/000/466/622/workout.mp4",
    ]
    domains = ["artstation.com"]
    pattern = REGEX_IMAGE
    id_name = ""
