from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.arca_live import ArcaLiveArtistUrl, ArcaLiveImageUrl, ArcaLivePostUrl, ArcaLiveUrl


class ArcaLiveParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ArcaLiveUrl | None:
        instance: ArcaLiveUrl
        match parsable_url.url_parts:

            # https://arca.live/b/arknights/66031722
            case "b", channel, post_id:
                instance = ArcaLivePostUrl(parsable_url)
                instance.post_id = int(post_id)
                instance.channel = channel

            # https://arca.live/u/@Si리링
            case "u", username, user_id if username.startswith("@"):
                instance = ArcaLiveArtistUrl(parsable_url)
                instance.user_id = int(user_id)
                instance.username = username.removeprefix("@")

            # https://arca.live/u/@Nauju/45320365
            case "u", username if username.startswith("@"):
                instance = ArcaLiveArtistUrl(parsable_url)
                instance.username = username.removeprefix("@")
                instance.user_id = None

            case _:
                return None
        return instance


class NamuLaParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ArcaLiveImageUrl | None:
        match parsable_url.url_parts:
            # https://ac2.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg
            # https://ac2.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig
            # https://ac2-o.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig
            # https://ac.namu.la/20221211sac/5ea7fbca5e49ec16beb099fc6fc991690d37552e599b1de8462533908346241e.png
            # https://ac-o.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.gif?type=orig
            # https://ac.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.mp4
            case date_string, filename:
                instance = ArcaLiveImageUrl(parsable_url)
                instance.date_string = date_string
                instance.filename = filename

            case _:
                return None

        return instance
