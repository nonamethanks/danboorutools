from danboorutools.logical.extractors.hentai_foundry import (HentaiFoundryArtistUrl, HentaiFoundryImageUrl, HentaiFoundryOldPostUrl,
                                                             HentaiFoundryPostUrl, HentaiFoundryUrl)
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class HentaiFoundryComParser(UrlParser):
    domains = ["hentai-foundry.com"]

    test_cases = {
        HentaiFoundryArtistUrl: [
            "https://www.hentai-foundry.com/user/kajinman",
            "https://www.hentai-foundry.com/user/kajinman/profile",
            "https://www.hentai-foundry.com/user/J-likes-to-draw/profile",

            "https://www.hentai-foundry.com/pictures/user/kajinman",
            "https://www.hentai-foundry.com/pictures/user/kajinman/scraps",

            "http://www.hentai-foundry.com/user-RockCandy.php",
            "http://www.hentai-foundry.com/profile-sawao.php",
        ],
        HentaiFoundryImageUrl: [
            "https://pictures.hentai-foundry.com/a/Afrobull/795025/Afrobull-795025-kuroeda.png",
            "https://pictures.hentai-foundry.com/_/-MadKaiser-/532792/-MadKaiser--532792-FFXIV_Miqote.png",

            "http://pictures.hentai-foundry.com//s/soranamae/363663.jpg",
            "http://www.hentai-foundry.com/piccies/d/dmitrys/1183.jpg",
        ],
        HentaiFoundryPostUrl: [
            "https://www.hentai-foundry.com/pictures/user/Afrobull/795025",
            "https://www.hentai-foundry.com/pictures/user/Afrobull/795025/kuroeda",
        ],
        HentaiFoundryOldPostUrl: [
            "https://thumbs.hentai-foundry.com/thumb.php?pid=795025&size=350",
            "http://www.hentai-foundry.com/pic-795025",
            "http://www.hentai-foundry.com/pic-149160.html",
            "http://www.hentai-foundry.com/pic-149160.php",
            "http://www.hentai-foundry.com/pic_full-66045.php",
            "http://www.hentai-foundry.com/pictures/151578/",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> HentaiFoundryUrl | None:
        instance: HentaiFoundryUrl

        match parsable_url.url_parts:
            case _, username, work_id, _ if work_id.isnumeric():
                instance = HentaiFoundryImageUrl(parsable_url)
                instance.username = username
                instance.work_id = int(work_id)
            case *_, subdir, username, work_id_filename if len(subdir) == 1:
                instance = HentaiFoundryImageUrl(parsable_url)
                instance.username = username
                instance.work_id = int(work_id_filename.split(".")[0])

            case "pictures", "user", username, work_id, *_ if work_id.isnumeric():
                instance = HentaiFoundryPostUrl(parsable_url)
                instance.username = username
                instance.work_id = int(work_id)

            case "pictures", "user", username, *_:
                instance = HentaiFoundryArtistUrl(parsable_url)
                instance.username = username

            case "user", username, *_:
                instance = HentaiFoundryArtistUrl(parsable_url)
                instance.username = username

            case "pictures", work_id:
                instance = HentaiFoundryOldPostUrl(parsable_url)
                instance.work_id = int(work_id)

            case artist_slug, if artist_slug.startswith("user-") or artist_slug.startswith("profile-"):
                instance = HentaiFoundryArtistUrl(parsable_url)
                instance.username = artist_slug.split(".")[0].split("-")[-1]

            case pic_slug, if pic_slug.startswith("pic-") or pic_slug.startswith("pic_"):
                instance = HentaiFoundryOldPostUrl(parsable_url)
                instance.work_id = int(pic_slug.split(".")[0].split("-")[-1])

            case "thumb.php", :
                instance = HentaiFoundryOldPostUrl(parsable_url)
                instance.work_id = int(parsable_url.params["pid"])

            case _:
                return None

        return instance
