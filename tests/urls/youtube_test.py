import pytest

from danboorutools.logical.urls import youtube as yt
from danboorutools.logical.urls.pixiv import PixivArtistUrl
from danboorutools.models.url import UselessUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test, generate_redirect_test

urls = {
    yt.YoutubeUserUrl: {
        "https://www.youtube.com/@Tripshots/featured": "https://www.youtube.com/@Tripshots",
    },
    yt.YoutubeChannelUrl: {
        "https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA": "https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA",
        "https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA/about": "https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA",
        "http://youtube.com/@channel/UCxw3WZ7N63dYExDwbZbHvqg": "https://www.youtube.com/channel/UCxw3WZ7N63dYExDwbZbHvqg",
    },
    yt.YoutubeOldUserUrl: {
        "https://www.youtube.com/c/kurasawakyosyo": "https://www.youtube.com/c/kurasawakyosyo",
        "https://www.youtube.com/user/speedosausage": "https://www.youtube.com/user/speedosausage",
        "https://www.youtube.com/c/LegendsofRuneterraKR/community": "https://www.youtube.com/c/LegendsofRuneterraKR",
        "https://consent.youtube.com/m?continue=https%3A%2F%2Fwww.youtube.com%2Fc%2Fchirosam%3Fcbrd%3D1&gl=DE&m=0&pc=yt&cm=4&hl=en&src=1": "https://www.youtube.com/c/chirosam",
    },
    yt.YoutubeVideoUrl: {
        "http://www.youtube.com/watch?v=qi6EePWYZlQ\u0026fmt=18": "https://www.youtube.com/watch?v=qi6EePWYZlQ",
        "https://www.youtube.com/watch?v=jZjONCvSjr0": "https://www.youtube.com/watch?v=jZjONCvSjr0",
        "https://www.youtube.com/shorts/jZjONCvSjr0": "https://www.youtube.com/watch?v=jZjONCvSjr0",
        "https://img.youtube.com/vi/vTPq-9k0m3A/maxresdefault.jpg": "https://www.youtube.com/watch?v=vTPq-9k0m3A",
        "http://youtu.be/fb90cRgI_ZQ": "https://www.youtube.com/watch?v=fb90cRgI_ZQ",
    },
    yt.YoutubeCommunityPostUrl: {
        "https://www.youtube.com/channel/UCMMBGMjrrWcRZmG_lW4jC-Q/community?lb=UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL": "https://www.youtube.com/channel/UCMMBGMjrrWcRZmG_lW4jC-Q/community?lb=UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL",
        "https://www.youtube.com/post/UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL": "https://www.youtube.com/post/UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL",
    },
    yt.YoutubePlaylistUrl: {
        "https://youtube.com/playlist?list=PLcw27-K4pcr23t305PlCpIYvulr0m2Agu": "https://www.youtube.com/playlist?list=PLcw27-K4pcr23t305PlCpIYvulr0m2Agu",
        "http://www.youtube.com/playlist?p=PL536F5620C09765C7": "https://www.youtube.com/playlist?list=PL536F5620C09765C7",
    },
    PixivArtistUrl: {
        "https://www.youtube.com/redirect?event=channel_description&redir_token=QUFFLUhqbmhHUm1HcUowbk8wUEJVZWJpWmRfck5yRUhWUXxBQ3Jtc0tuankwTXo2TTRYMFJNdDNwbnpUZ193Vk45b3FCVGxMcDNva1Rzby1wT1J1YUZpdTFRN0RvallTN0xwYUxYQXNWS1dvNU5wRExpZ0FBT2xxUTlUOGJ4TFNpcGptQ2xoVHpaUmtWTVI2WWhlNFhSZ1hEVQ&q=https%3A%2F%2Fwww.pixiv.net%2Fusers%2F37422": "https://www.pixiv.net/en/users/37422",
    },
    UselessUrl: {
        "https://www.youtube.com/results?search_query=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8Fch&sp=EgIIBA%253D%253D": "https://www.youtube.com/results?search_query=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8Fch&sp=EgIIBA%253D%253D",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://www.youtube.com/@niku_kai29",
        url_type=yt.YoutubeUserUrl,
        url_properties=dict(username="niku_kai29"),
        primary_names=["おにくちゃん(肉斬り包丁)"],
        secondary_names=["niku_kai29"],
        related=["https://twitter.com/niku_kai29", "https://seiga.nicovideo.jp/user/illust/59309002",
                 "https://www.pixiv.net/en/users/61603554"],
    )


def test_artist_url_2():
    generate_artist_test(
        url_string="https://www.youtube.com/@user-zb6db2qg1v",
        url_type=yt.YoutubeUserUrl,
        url_properties=dict(username="user-zb6db2qg1v"),
        primary_names=["のんのん"],
        secondary_names=[],
        related=[],
    )


def test_artist_url_3():
    generate_artist_test(
        url_string="https://www.youtube.com/@TheBrothresGreen2022Wonder",
        url_type=yt.YoutubeUserUrl,
        url_properties=dict(username="TheBrothresGreen2022Wonder"),
        primary_names=["The BrothresGreen!"],
        secondary_names=["TheBrothresGreen2022Wonder"],
        related=[
            "https://instagram.com/brothres_green",
            "https://deviantart.com/diamondgreenanimat0",
            "https://facebook.com/DiamondGreen_Art-2255991581322759/?modal=admin_todo_tour",
            "https://www.derpibooru.org/profiles/Brothresgreen_",
            "https://furaffinity.net/user/brothresgreen",
            "https://twitter.com/irene_coreas",
            "https://tiktok.com/@green_brothres",
        ],

    )


def test_redirect_url_1():
    generate_redirect_test(
        url_string="https://www.youtube.com/channel/UC6iCJQVd1TBBMvL2G9ML-Zg",
        url_type=yt.YoutubeChannelUrl,
        url_properties=dict(channel_id="UC6iCJQVd1TBBMvL2G9ML-Zg"),
        redirects_to="https://www.youtube.com/@niku_kai29",
    )


def test_redirect_url_2():
    generate_redirect_test(
        url_string="https://www.youtube.com/channel/UClcMRpGblRVpQs06Rv7tylA",
        url_type=yt.YoutubeChannelUrl,
        url_properties=dict(channel_id="UClcMRpGblRVpQs06Rv7tylA"),
        redirects_to="https://www.youtube.com/@user-zb6db2qg1v",
    )


def test_redirect_url_3():
    generate_redirect_test(
        url_string="https://www.youtube.com/channel/UC8U8Tv6xSPwV8Mout7ZIZ8A/about",
        url_type=yt.YoutubeChannelUrl,
        url_properties=dict(channel_id="UC8U8Tv6xSPwV8Mout7ZIZ8A"),
        redirects_to="https://www.youtube.com/@TheBrothresGreen2022Wonder",
    )
