from danboorutools.logical.urls import naver as n
from tests.urls import assert_artist_url, assert_redirect_url, generate_parsing_suite

urls = {
    n.NaverBlogArtistUrl: {
        "http://m.blog.naver.com/kirbystar": "https://blog.naver.com/kirbystar",
        "https://blog.naver.com/guestbook/GuestBookList.naver?blogId=doremi4704": "https://blog.naver.com/doremi4704",
        "https://blog.naver.com/profile/intro.nhn?blogId=gyul_acc": "https://blog.naver.com/gyul_acc",
        "http://section.blog.naver.com/connect/ViewMoreBuddyPosts.nhn?blogId=mimi2340&widgetSeq=47847": "https://blog.naver.com/mimi2340",
        "https://blog.naver.com/NBlogTop.naver?isHttpsRedirect=true&blogId=zoncrown": "https://blog.naver.com/zoncrown",
    },
    n.NaverBlogPostUrl: {
        "http://blog.naver.com/cherrylich/70163410487": "https://blog.naver.com/cherrylich/70163410487",
        "http://blog.naver.com/PostView.nhn?blogId=mocu00&logNo=130121996977&redirect=Dlog": "https://blog.naver.com/mocu00/130121996977",
        "http://blog.naver.com/PostPrint.nhn?blogId=amejaga&logNo=221155304992#": "https://blog.naver.com/amejaga/221155304992",
        "http://blog.naver.com/PostThumbnailView.nhn?blogId=evildice&logNo=130179909109&categoryNo=1&parentCategoryNo=1&from=postList": "https://blog.naver.com/evildice/130179909109",
    },
    n.NaverPostArtistUrl: {
        "https://post.naver.com/parang9494": "https://post.naver.com/parang9494",
    },
    n.NaverPostArtistWithIdUrl: {
        "https://post.naver.com/my.nhn?memberNo=6072169": "https://post.naver.com/my.nhn?memberNo=6072169",
    },
    n.NaverPostPostUrl: {
        "https://post.naver.com/viewer/postView.nhn?volumeNo=16039891&memberNo=7662880": "https://post.naver.com/viewer/postView.nhn?volumeNo=16039891&memberNo=7662880",
    },
    n.NaverComicArtistUrl: {
        "http://comic.naver.com/artistTitle.nhn?artistId=274812": "https://comic.naver.com/artistTitle?artistId=274812",
    },
    n.NaverComicUrl: {
        "http://comic.naver.com/webtoon/list.nhn?titleId=183559&no=46&weekday=mon": "https://comic.naver.com/webtoon/list?titleId=183559",
        "http://comic.naver.com/webtoon/list?titleId=183559&no=46&weekday=mon": "https://comic.naver.com/webtoon/list?titleId=183559",
        "https://comic.naver.com/bestChallenge/list?titleId=717924": "https://comic.naver.com/bestChallenge/list?titleId=717924",
    },
    n.NaverComicChapterUrl: {
        "https://comic.naver.com/webtoon/detail?titleId=183559&no=46&weekday=mon": "https://comic.naver.com/webtoon/detail?titleId=183559&no=46",
        "https://comic.naver.com/webtoon/detail.nhn?titleId=183559&no=46&weekday=mon": "https://comic.naver.com/webtoon/detail?titleId=183559&no=46",
        "https://comic.naver.com/bestChallenge/detail?titleId=717924&no=34": "https://comic.naver.com/bestChallenge/detail?titleId=717924&no=34",
    },
    n.NaverCafeArtistUrl: {
        "http://cafe.naver.com/brushonacademy/": "https://cafe.naver.com/brushonacademy",
    },
    n.NaverCafeArtistWithIdUrl: {
        "https://cafe.naver.com/ca-fe/cafes/27807122/members/wuEFQlBuDP4vM30IcO5Maw": "https://cafe.naver.com/MyCafeIntro.nhn?clubid=27807122",
    },
    n.NaverCafePostUrl: {
        "https://cafe.naver.com/brushonacademy/4423": "https://cafe.naver.com/brushonacademy/4423",
    },
    n.NaverCafePostWithArtistIdUrl: {
        "https://cafe.naver.com/ArticleRead.nhn?clubid=29039136&articleid=2817624&": "https://cafe.naver.com/ca-fe/cafes/29039136/articles/2817624",
        "https://cafe.naver.com/ca-fe/cafes/29767250/articles/388": "https://cafe.naver.com/ca-fe/cafes/29767250/articles/388",
        "https://m.cafe.naver.com/ca-fe/web/cafes/10947985/articles/204011?art=aW50ZXJuYWwtY2FmZS13ZWItc2VjdGlvbi1zZWFyY2gtbGlzdA.eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjYWZlVHlwZSI6IkNBRkVfVVJMIiwiYXJ0aWNsZUlkIjoyMDQwMTEsImNhZmVVcmwiOiJvaHdvdyIsImlzc3VlZEF0IjoxNjk3MDg1NjIzNDMxfQ.u2UbcjPRkICdt59GrJUuRGxkjL1wwMIkmkLBHrBPp0w&q=섀도우댄서%09&tc=section_search_result_articles": "https://cafe.naver.com/ca-fe/cafes/10947985/articles/204011"
    },
    n.NaverGrafolioArtistUrl: {
        "https://grafolio.naver.com/taccachantrieri13art": "https://grafolio.naver.com/taccachantrieri13art",
    },
    n.NaverGrafolioPostUrl: {
        "https://grafolio.naver.com/works/896565": "https://grafolio.naver.com/works/896565",
    },
    n.NaverRedirectUrl: {
        "https://naver.me/xKCzsue4": "https://naver.me/xKCzsue4",
    },
    n.NaverTvUrl: {
        "http://tv.naver.com/paper": "https://tv.naver.com/paper",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    url="https://blog.naver.com/evildice/",
    url_type=n.NaverBlogArtistUrl,
    url_properties=dict(username="evildice"),
    primary_names=["콜드림"],
    secondary_names=["evildice"],
    related=[],
)


assert_redirect_url(
    "https://cafe.naver.com/ca-fe/cafes/27807122/members/wuEFQlBuDP4vM30IcO5Maw",
    url_type=n.NaverCafeArtistWithIdUrl,
    url_properties=dict(user_id=27807122),
    redirects_to="https://cafe.naver.com/brushonacademy/",
)

assert_redirect_url(
    "https://post.naver.com/my.nhn?memberNo=9055207",
    url_type=n.NaverPostArtistWithIdUrl,
    url_properties=dict(user_id=9055207),
    redirects_to="https://post.naver.com/parang9494",
)


assert_redirect_url(
    "https://cafe.naver.com/ca-fe/cafes/29767250/articles/388",
    url_type=n.NaverCafePostWithArtistIdUrl,
    url_properties=dict(user_id=29767250, post_id=388),
    redirects_to="https://cafe.naver.com/nexonmoe/388",
)
