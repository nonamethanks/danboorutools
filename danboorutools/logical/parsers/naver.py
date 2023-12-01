from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import naver as n
from danboorutools.models.url import UnsupportedUrl, Url


class NaverComParser(UrlParser):
    PAGE_SUFFIXES = (".nhn", ".naver", ".html", ".jsp")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.subdomain.split(".")[-1]:
            case "blog":
                return cls._match_blog(parsable_url)
            case "comic":
                return cls._match_comic(parsable_url)
            case "cafe":
                return cls._match_cafe(parsable_url)
            case "grafolio":
                return cls._match_grafolio(parsable_url)
            case "post":
                return cls._match_post(parsable_url)
            case "tv":
                return cls._match_tv(parsable_url)
            # https://closers.nexon.game.naver.com/Ucc/WebToon/List?emSearchType=WriterName&strSearch=%ED%8B%B0%EC%95%84%EC%85%B0
            case "game":
                return UnsupportedUrl(parsed_url=parsable_url)
            # https://patron.naver.com/grafolio/p/intro/138694
            case "patron":
                url = UnsupportedUrl(parsed_url=parsable_url)
                url.is_deleted = True
                return url
            # https://smartstore.naver.com/caffestrega/products/8248776543
            case "smartstore":
                return UnsupportedUrl(parsed_url=parsable_url)
            case _:
                return None

    @classmethod
    def _match_blog(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # http://blog.naver.com/cherrylich/70163410487
            case username, post_id if not parsable_url.url_parts[-1].endswith(cls.PAGE_SUFFIXES):
                return n.NaverBlogPostUrl(parsed_url=parsable_url,
                                          username=username,
                                          post_id=int(post_id))

            # http://m.blog.naver.com/kirbystar
            case username, if not username.endswith(cls.PAGE_SUFFIXES):
                return n.NaverBlogArtistUrl(parsed_url=parsable_url,
                                            username=username)

            # http://blog.naver.com/PostList.nhn?blogId=dbs082174
            # https://blog.naver.com/NBlogTop.naver?isHttpsRedirect=true&blogId=zoncrown
            case ("PostList.nhn" | "PostList.naver" | "NBlogTop.naver"), :
                return n.NaverBlogArtistUrl(parsed_url=parsable_url,
                                            username=parsable_url.query["blogId"])

            # https://blog.naver.com/guestbook/GuestBookList.naver?blogId=doremi4704
            # http://section.blog.naver.com/connect/ViewMoreBuddyPosts.nhn?blogId=mimi2340&widgetSeq=47847
            # http://blog.naver.com/prologue/PrologueList.nhn?blogId=tobsua
            case ("profile", "intro.nhn") |\
                 ("guestbook", "GuestBookList.naver") |\
                 ("connect", "ViewMoreBuddyPosts.nhn") |\
                 ("prologue", "PrologueList.nhn"):
                return n.NaverBlogArtistUrl(parsed_url=parsable_url,
                                            username=parsable_url.query["blogId"])

            # http://blog.naver.com/PostView.nhn?blogId=mocu00&logNo=130121996977&redirect=Dlog
            # http://blog.naver.com/PostPrint.nhn?blogId=amejaga&logNo=221155304992#
            # http://blog.naver.com/PostThumbnailView.nhn?blogId=evildice&logNo=130179909109&categoryNo=1&parentCategoryNo=1&from=postList
            case ("PostView.nhn" | "PostView.naver" | "PostPrint.nhn" | "PostThumbnailView.nhn"), :
                return n.NaverBlogPostUrl(parsed_url=parsable_url,
                                          username=parsable_url.query["blogId"],
                                          post_id=int(parsable_url.query["logNo"].strip("#")))

            # http://blog.naver.com/storyphoto/viewer.html?src=http%3A%2F%2Fblogfiles.naver.net%2F20120511_129%2Falien1452_1336672455921qtcwI_JPEG%2F2012alien15-1.jpg
            case "storyphoto", ("viewer.html" | "viewer.jsp"):
                return cls.parse(parsable_url.query["src"])

            case _:
                return None

    @staticmethod
    def _match_comic(parsable_url: ParsableUrl) -> n.NaverUrl | None:
        match parsable_url.url_parts:
            # http://comic.naver.com/artistTitle.nhn?artistId=274812
            case "artistTitle.nhn", :
                return n.NaverComicArtistUrl(parsed_url=parsable_url,
                                             artist_id=int(parsable_url.query["artistId"]))

            # http://comic.naver.com/webtoon/list?titleId=183559&no=46&weekday=mon
            # http://comic.naver.com/webtoon/list.nhn?titleId=183559&no=46&weekday=mon
            # https://comic.naver.com/bestChallenge/list?titleId=717924
            case comic_type, ("list" | "list.nhn"):
                return n.NaverComicUrl(parsed_url=parsable_url,
                                       comic_id=int(parsable_url.query["titleId"]),
                                       comic_type=comic_type)

            # https://comic.naver.com/webtoon/detail?titleId=183559&no=46&weekday=mon
            # https://comic.naver.com/webtoon/detail.nhn?titleId=183559&no=46&weekday=mon
            # https://comic.naver.com/bestChallenge/detail?titleId=717924&no=34
            case comic_type, ("detail" | "detail.nhn"):
                return n.NaverComicChapterUrl(parsed_url=parsable_url,
                                              chapter_id=int(parsable_url.query["no"]),
                                              comic_id=int(parsable_url.query["titleId"]),
                                              comic_type=comic_type)

            case _:
                return None

    @classmethod
    def _match_cafe(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # https://cafe.naver.com/brushonacademy/4423
            case username, post_id if not username.endswith(cls.PAGE_SUFFIXES):
                return n.NaverCafePostUrl(parsed_url=parsable_url,
                                          username=username,
                                          post_id=int(post_id))

            # http://cafe.naver.com/brushonacademy/
            case username, if not username.endswith(cls.PAGE_SUFFIXES):
                return n.NaverCafeArtistUrl(parsed_url=parsable_url,
                                            username=username)

            # https://cafe.naver.com/MyCafeIntro.nhn?clubid=27842958
            case "MyCafeIntro.nhn", :
                return n.NaverCafeArtistWithIdUrl(parsed_url=parsable_url,
                                                  user_id=int(parsable_url.query["clubid"]))

            # https://cafe.naver.com/ca-fe/cafes/27842958/members/_R65HL2nWXGpN38PNiHXww
            case "ca-fe", "cafes", user_id, "members", _:
                return n.NaverCafeArtistWithIdUrl(parsed_url=parsable_url,
                                                  user_id=int(user_id))

            # https://cafe.naver.com/ca-fe/cafes/29767250/articles/388
            # https://m.cafe.naver.com/ca-fe/web/cafes/10947985/articles/204011?art=aW50ZXJuYWwtY2FmZS13ZWItc2VjdGlvbi1zZWFyY2gtbGlzdA.eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjYWZlVHlwZSI6IkNBRkVfVVJMIiwiYXJ0aWNsZUlkIjoyMDQwMTEsImNhZmVVcmwiOiJvaHdvdyIsImlzc3VlZEF0IjoxNjk3MDg1NjIzNDMxfQ.u2UbcjPRkICdt59GrJUuRGxkjL1wwMIkmkLBHrBPp0w&q=섀도우댄서%09&tc=section_search_result_articles
            case "ca-fe", *_, "cafes", user_id, "articles", article_id:
                return n.NaverCafePostWithArtistIdUrl(parsed_url=parsable_url,
                                                      user_id=int(user_id),
                                                      post_id=int(article_id))

            # https://cafe.naver.com/ArticleRead.nhn?clubid=29039136&articleid=2817624&
            case "ArticleRead.nhn", :
                return n.NaverCafePostWithArtistIdUrl(parsed_url=parsable_url,
                                                      user_id=int(parsable_url.query["clubid"]),
                                                      post_id=int(parsable_url.query["articleid"]))

            # https://m.cafe.naver.com/ImageView.nhn?imageUrl=https://mcafethumb-phinf.pstatic.net/MjAxOTAyMDFfNTUg/MDAxNTQ5MDA1OTY0NjEx.vduZYz_zgFhQ7OAV3rwFHLmWWrCYfi1O4POPR-zFcGQg.HL6HTEOChD7OzRCzgTCtgdgSeZ8xcbqHsniRZyw-HJkg.JPEG.nfgames/%25ED%2598%2588%25EB%259D%25BC%25EB%258B%2598.jpg
            case "ImageView.nhn", :
                return cls.parse(parsable_url.query["imageUrl"])

            # https://cafe.naver.com/common/storyphoto/viewer.html?src=https%3A%2F%2Fcafeptthumb-phinf.pstatic.net%2FMjAyMzA3MDZfMzIg%2FMDAxNjg4NjM3NzcyNDg3.CrtekTl5XiXEJCFy9532vabMKo0CaWwryTMM0Up77Jgg.8ppf2Q3uiVWUlIP6jckYwYSe5Ys-erSsd7yf8XoHECIg.PNG%2F%25EC%259C%25A0%25EC%259A%25B0%25EC%25B9%25B4_%25EC%2597%2585%25EB%25A1%259C%25EB%2593%259C%25EC%259A%25A9.png
            case "common", "storyphoto", "viewer.html":
                return cls.parse(parsable_url.query["src"])

            case _:
                return None

    @classmethod
    def _match_grafolio(cls, parsable_url: ParsableUrl) -> n.NaverUrl | None:
        match parsable_url.url_parts:
            # https://grafolio.naver.com/taccachantrieri13art
            case username, if not username.endswith(cls.PAGE_SUFFIXES):
                return n.NaverGrafolioArtistUrl(parsed_url=parsable_url,
                                                username=username)

            # https://grafolio.naver.com/works/896565
            case "works", post_id:
                return n.NaverGrafolioPostUrl(parsed_url=parsable_url,
                                              post_id=int(post_id))

            case _:
                return None

    @classmethod
    def _match_post(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # http://post.naver.com/parang9494
            case username, if not username.endswith(cls.PAGE_SUFFIXES):
                return n.NaverPostArtistUrl(parsed_url=parsable_url,
                                            username=username)

            # https://post.naver.com/my.nhn?memberNo=6072169
            case "my.nhn", :
                return n.NaverPostArtistWithIdUrl(parsed_url=parsable_url,
                                                  user_id=int(parsable_url.query["memberNo"]))

            # https://post.naver.com/viewer/postView.nhn?volumeNo=16039891&memberNo=7662880
            case "viewer", "postView.nhn":
                return n.NaverPostPostUrl(parsed_url=parsable_url,
                                          user_id=int(parsable_url.query["memberNo"]),
                                          post_id=int(parsable_url.query["volumeNo"]))

            case "viewer", "image.nhn":
                return cls.parse(parsable_url.query["src"])

            case _:
                return None

    @classmethod
    def _match_tv(cls, parsable_url: ParsableUrl) -> n.NaverUrl | None:
        match parsable_url.url_parts:
            # http://tv.naver.com/paper
            case username, if not username.endswith(cls.PAGE_SUFFIXES):
                return n.NaverTvUrl(parsed_url=parsable_url,
                                    username=username)

            case _:
                return None


class NaverMeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> n.NaverRedirectUrl | None:
        match parsable_url.url_parts:
            # https://naver.me/xKCzsue4
            case redirect_id, :
                return n.NaverRedirectUrl(parsed_url=parsable_url,
                                          redirect_id=redirect_id)
            case _:
                return None
