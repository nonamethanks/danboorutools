from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.hentai_foundry import (
    HentaiFoundryArtistUrl,
    HentaiFoundryImageUrl,
    HentaiFoundryOldPostUrl,
    HentaiFoundryPostUrl,
    HentaiFoundryUrl,
)


class HentaiFoundryComParser(UrlParser):
    domains = ["hentai-foundry.com"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> HentaiFoundryUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:

            # https://pictures.hentai-foundry.com/a/Afrobull/795025/Afrobull-795025-kuroeda.png
            # https://pictures.hentai-foundry.com/_/-MadKaiser-/532792/-MadKaiser--532792-FFXIV_Miqote.png
            case _, username, post_id, _ if post_id.isnumeric():
                return HentaiFoundryImageUrl(parsed_url=parsable_url,
                                             username=username,
                                             work_id=int(post_id))

            # http://pictures.hentai-foundry.com//s/soranamae/363663.jpg
            # http://www.hentai-foundry.com/piccies/d/dmitrys/1183.jpg
            case *_, subdir, username, _filename if len(subdir) == 1:
                return HentaiFoundryImageUrl(parsed_url=parsable_url,
                                             username=username,
                                             work_id=int(parsable_url.stem))

            # https://www.hentai-foundry.com/pictures/user/Afrobull/795025
            # https://www.hentai-foundry.com/pictures/user/Afrobull/795025/kuroeda
            case "pictures", "user", username, post_id, *_ if post_id.isnumeric():
                return HentaiFoundryPostUrl(parsed_url=parsable_url,
                                            username=username,
                                            post_id=int(post_id))

            # https://www.hentai-foundry.com/pictures/user/kajinman
            # https://www.hentai-foundry.com/pictures/user/kajinman/scraps
            case "pictures", "user", username, *_:
                return HentaiFoundryArtistUrl(parsed_url=parsable_url,
                                              username=username)

            # https://www.hentai-foundry.com/user/kajinman
            # https://www.hentai-foundry.com/user/kajinman/profile
            # https://www.hentai-foundry.com/user/J-likes-to-draw/profile
            case "user", username, *_:
                return HentaiFoundryArtistUrl(parsed_url=parsable_url,
                                              username=username)

            # http://www.hentai-foundry.com/pictures/151578/
            case "pictures", post_id:
                return HentaiFoundryOldPostUrl(parsed_url=parsable_url,
                                               post_id=int(post_id))

            # http://www.hentai-foundry.com/user-RockCandy.php
            # http://www.hentai-foundry.com/profile-sawao.php
            case artist_slug, if artist_slug.startswith(("user-", "profile-")):
                return HentaiFoundryArtistUrl(parsed_url=parsable_url,
                                              username=parsable_url.stem.split("-")[-1])

            # http://www.hentai-foundry.com/pic-795025
            # http://www.hentai-foundry.com/pic-149160.html
            # http://www.hentai-foundry.com/pic-149160.php
            # http://www.hentai-foundry.com/pic_full-66045.php
            case pic_slug, if pic_slug.startswith(("pic-", "pic_")):
                return HentaiFoundryOldPostUrl(parsed_url=parsable_url,
                                               post_id=int(parsable_url.stem.split("-")[-1]))

            # https://thumbs.hentai-foundry.com/thumb.php?pid=795025&size=350
            case "thumb.php", :
                return HentaiFoundryOldPostUrl(parsed_url=parsable_url,
                                               post_id=int(parsable_url.query["pid"]))

            case _:
                return None
