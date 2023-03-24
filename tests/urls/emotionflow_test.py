from danboorutools.logical.urls.emotionflow import EmotionflowArtistUrl, EmotionflowImageUrl, EmotionflowPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    EmotionflowArtistUrl: {
        "https://galleria.emotionflow.com/72085/profile.html": "https://galleria.emotionflow.com/72085/",
        "https://galleria.emotionflow.com/72085/": "https://galleria.emotionflow.com/72085/",
        "http://temp.emotionflow.com/2153/": "https://galleria.emotionflow.com/2153/",
        "http://galleria.emotionflow.com/GalleryListGridV.jsp?ID=15878": "https://galleria.emotionflow.com/15878/",
        "http://galleria.emotionflow.com/s/GalleryListGridV.jsp?ID=31946": "https://galleria.emotionflow.com/31946/",
    },
    EmotionflowPostUrl: {
        "https://galleria.emotionflow.com/87607/662619.html": "https://galleria.emotionflow.com/87607/662619.html",
        "http://galleria.emotionflow.com/CommentDetailV.jsp?ID=36717\u0026TD=346099\u0026CD=205472": "https://galleria.emotionflow.com/36717/346099.html",
        "http://galleria.emotionflow.com/IllustDetailV.jsp?ID=15641\u0026TD=347301": "https://galleria.emotionflow.com/15641/347301.html",
    },
    EmotionflowImageUrl: {
        "http://img01.emotionflow.com/galleria/user_img6/13998/1399816168590955.jpeg": "https://galleria-img.emotionflow.com/user_img6/13998/1399816168590955.jpeg",
        "http://galleria-img.emotionflow.com/user_img9/87607/i662619_308.jpeg_360.jpg?0315104612": "https://galleria-img.emotionflow.com/user_img9/87607/i662619_308.jpeg",
        "https://galleria.emotionflow.com/user_img9/40091/i477242_677.png": "https://galleria-img.emotionflow.com/user_img9/40091/i477242_677.png",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://galleria.emotionflow.com/72085/",
    url_type=EmotionflowArtistUrl,
    url_properties=dict(user_id=72085),
    primary_names=["karadaganai"],
    secondary_names=[],
    related=[],
)
