from danboorutools.logical.extractors import youtube as yt
from danboorutools.logical.extractors.pixiv import PixivArtistUrl
from danboorutools.models.url import UselessUrl
from tests.extractors import assert_artist_url, assert_redirect_url, generate_parsing_suite

urls = {
    yt.YoutubeUserUrl: {
        "https://www.youtube.com/@Tripshots/featured": "https://www.youtube.com/@Tripshots",
    },
    yt.YoutubeChannelUrl: {
        "https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA": "https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA",
        "https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA/about": "https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA",
    },
    yt.YoutubeOldUserUrl: {
        "https://www.youtube.com/c/kurasawakyosyo": "https://www.youtube.com/c/kurasawakyosyo",
        "https://www.youtube.com/user/speedosausage": "https://www.youtube.com/user/speedosausage",
        "https://www.youtube.com/c/LegendsofRuneterraKR/community": "https://www.youtube.com/c/LegendsofRuneterraKR",
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


generate_parsing_suite(urls)


assert_redirect_url(
    "https://www.youtube.com/channel/UC6iCJQVd1TBBMvL2G9ML-Zg",
    url_type=yt.YoutubeChannelUrl,
    url_properties=dict(channel_id="UC6iCJQVd1TBBMvL2G9ML-Zg"),
    redirects_to="https://www.youtube.com/@niku_kai29",
)


assert_artist_url(
    "https://www.youtube.com/@niku_kai29",
    url_type=yt.YoutubeUserUrl,
    url_properties=dict(username="niku_kai29"),
    primary_names=["エヴァンゲリオン斬り(肉斬り包丁)"],
    secondary_names=["niku_kai29"],
    related=["https://twitter.com/niku_kai29", "https://seiga.nicovideo.jp/user/illust/59309002",
             "https://www.pixiv.net/en/users/61603554"],
)
