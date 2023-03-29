import re

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.emotionflow import EmotionflowArtistUrl, EmotionflowImageUrl, EmotionflowPostUrl, EmotionflowUrl


class EmotionflowComParser(UrlParser):
    old_image_subdomain = re.compile(r"^img\d+$")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EmotionflowUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://galleria.emotionflow.com/72085/
            case user_id, if user_id.isnumeric():
                return EmotionflowArtistUrl(parsed_url=parsable_url,
                                            user_id=int(user_id))

            # http://galleria.emotionflow.com/s/GalleryListGridV.jsp?ID=31946
            case "s", *_:
                return cls.match_url(parsable_url.without("s"))

            # https://galleria.emotionflow.com/72085/profile.html
            # https://galleria.emotionflow.com/72085/gallery.html
            case user_id, ("profile.html" | "gallery.html"):
                return EmotionflowArtistUrl(parsed_url=parsable_url,
                                            user_id=int(user_id))

            # https://galleria.emotionflow.com/87607/662619.html
            case user_id, post_id:
                return EmotionflowPostUrl(parsed_url=parsable_url,
                                          user_id=int(user_id),
                                          post_id=int(post_id.removesuffix(".html")))

            # http://galleria.emotionflow.com/s/GalleryListGridV.jsp?ID=31946
            case "GalleryListGridV.jsp", :
                return EmotionflowArtistUrl(parsed_url=parsable_url,
                                            user_id=int(parsable_url.query["ID"]))

            # http://galleria.emotionflow.com/CommentDetailV.jsp?ID=36717\u0026TD=346099\u0026CD=205472
            # http://galleria.emotionflow.com/IllustDetailV.jsp?ID=15641\u0026TD=347301
            case ("CommentDetailV.jsp" | "IllustDetailV.jsp"), :
                return EmotionflowPostUrl(parsed_url=parsable_url,
                                          user_id=int(parsable_url.query["ID"]),
                                          post_id=int(parsable_url.query["TD"]))

            # https://galleria-img.emotionflow.com/user_img9/55682/c577948_901.png
            case subdir, user_id, _filename if parsable_url.subdomain in ["galleria-img", "galleria"]:
                return EmotionflowImageUrl(parsed_url=parsable_url,
                                           user_id=int(user_id),
                                           subdir=subdir)

            # http://img01.emotionflow.com/galleria/user_img6/13998/1399816168590955.jpeg
            case "galleria", subdir, user_id, _filename if cls.old_image_subdomain.match(parsable_url.subdomain):
                return EmotionflowImageUrl(parsed_url=parsable_url,
                                           user_id=int(user_id),
                                           subdir=subdir)

            case _:
                return None
