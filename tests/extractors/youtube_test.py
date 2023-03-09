from danboorutools.logical.extractors import youtube as yt
from tests.extractors import generate_parsing_suite

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
    },
    yt.YoutubeCommunityPostUrl: {
        "https://www.youtube.com/channel/UCMMBGMjrrWcRZmG_lW4jC-Q/community?lb=UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL": "https://www.youtube.com/channel/UCMMBGMjrrWcRZmG_lW4jC-Q/community?lb=UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL",
        "https://www.youtube.com/post/UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL": "https://www.youtube.com/post/UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL",
    },
}


generate_parsing_suite(urls)
