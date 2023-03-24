from danboorutools.logical.urls.naver import NaverBlogArtistUrl, NaverBlogPostUrl, NaverCafeArtistUrl, NaverCafePostUrl
from tests.urls import generate_parsing_suite

urls = {
    NaverCafeArtistUrl: {
    },
    NaverCafePostUrl: {
        "http://cafe.naver.com/odiaacademy/23": "http://cafe.naver.com/odiaacademy/23",
    },
    NaverBlogArtistUrl: {
        "http://blog.naver.com/redlhzz": "http://blog.naver.com/redlhzz",
    },
    NaverBlogPostUrl: {
    },
}


generate_parsing_suite(urls)
