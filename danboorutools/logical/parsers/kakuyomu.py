from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.kakuyomu import KakuyomuArtistUrl, KakuyomuPostUrl, KakuyomuUrl


class KakuyomuJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> KakuyomuUrl | None:
        match parsable_url.url_parts:
            # http://kakuyomu.jp/users/a_yanagi
            # https://kakuyomu.jp/users/i_s/works/
            case "users", username, *_:
                return KakuyomuArtistUrl(parsed_url=parsable_url,
                                                  username=username)
            # https://kakuyomu.jp/works/1177354054883348735
            case "works", work_id:
                return KakuyomuPostUrl(parsed_url=parsable_url,
                                       post_id=int(work_id))

            # https://kakuyomu.jp/works/1177354054882921926/episodes/1177354054884254424
            case _:
                return None
