from danboorutools.logical.extractors.tumblr import TumblrArtistUrl, TumblrImageUrl, TumblrPostRedirectUrl, TumblrPostUrl
from tests.extractors import assert_artist_url, generate_parsing_suite

urls = {
    TumblrArtistUrl: {
        "https://www.tumblr.com/blog/view/artofelaineho": "https://artofelaineho.tumblr.com",
        "https://tumblr.com/blog/view/artofelaineho": "https://artofelaineho.tumblr.com",
        "https://www.tumblr.com/blog/artofelaineho": "https://artofelaineho.tumblr.com",
        "http://tumblr.com/blog/kervalchan": "https://kervalchan.tumblr.com",
        "https://www.tumblr.com/dashboard/blog/dankwartart": "https://dankwartart.tumblr.com",
        "https://tumblr.com/dashboard/blog/dankwartart": "https://dankwartart.tumblr.com",
        "https://www.tumblr.com/tawni-tailwind": "https://tawni-tailwind.tumblr.com",
        "https://tumblr.com/tawni-tailwind": "https://tawni-tailwind.tumblr.com",

        "https://rosarrie.tumblr.com/archive": "https://rosarrie.tumblr.com",
        "https://solisnotte.tumblr.com/about": "https://solisnotte.tumblr.com",
        "http://whereisnovember.tumblr.com/tagged/art": "https://whereisnovember.tumblr.com",
    },

    TumblrImageUrl: {
        "https://66.media.tumblr.com/168dabd09d5ad69eb5fedcf94c45c31a/3dbfaec9b9e0c2e3-72/s640x960/bf33a1324f3f36d2dc64f011bfeab4867da62bc8.png": "https://66.media.tumblr.com/168dabd09d5ad69eb5fedcf94c45c31a/3dbfaec9b9e0c2e3-72/s21000x21000/bf33a1324f3f36d2dc64f011bfeab4867da62bc8.png",
        "https://66.media.tumblr.com/5a2c3fe25c977e2281392752ab971c90/3dbfaec9b9e0c2e3-92/s500x750/4f92bbaaf95c0b4e7970e62b1d2e1415859dd659.png": "https://66.media.tumblr.com/5a2c3fe25c977e2281392752ab971c90/3dbfaec9b9e0c2e3-92/s21000x21000/4f92bbaaf95c0b4e7970e62b1d2e1415859dd659.png",
        # "http://data.tumblr.com/07e7bba538046b2b586433976290ee1f/tumblr_o3gg44HcOg1r9pi29o1_raw.jpg": "http://data.tumblr.com/07e7bba538046b2b586433976290ee1f/tumblr_o3gg44HcOg1r9pi29o1_raw.jpg",
        # "https://40.media.tumblr.com/de018501416a465d898d24ad81d76358/tumblr_nfxt7voWDX1rsd4umo1_r23_1280.jpg": "https://40.media.tumblr.com/de018501416a465d898d24ad81d76358/tumblr_nfxt7voWDX1rsd4umo1_r23_1280.jpg",
        # "https://media.tumblr.com/de018501416a465d898d24ad81d76358/tumblr_nfxt7voWDX1rsd4umo1_r23_raw.jpg": "https://media.tumblr.com/de018501416a465d898d24ad81d76358/tumblr_nfxt7voWDX1rsd4umo1_r23_raw.jpg",
        # "https://66.media.tumblr.com/2c6f55531618b4335c67e29157f5c1fc/tumblr_pz4a44xdVj1ssucdno1_1280.png": "https://66.media.tumblr.com/2c6f55531618b4335c67e29157f5c1fc/tumblr_pz4a44xdVj1ssucdno1_1280.png",
        # "https://68.media.tumblr.com/ee02048f5578595badc95905e17154b4/tumblr_inline_ofbr4452601sk4jd9_250.gif": "https://68.media.tumblr.com/ee02048f5578595badc95905e17154b4/tumblr_inline_ofbr4452601sk4jd9_250.gif",
        # "https://media.tumblr.com/ee02048f5578595badc95905e17154b4/tumblr_inline_ofbr4452601sk4jd9_500.gif": "https://media.tumblr.com/ee02048f5578595badc95905e17154b4/tumblr_inline_ofbr4452601sk4jd9_500.gif",
        # "https://66.media.tumblr.com/b9395771b2d0435fe4efee926a5a7d9c/tumblr_pg2wu1L9DM1trd056o2_500h.png": "https://66.media.tumblr.com/b9395771b2d0435fe4efee926a5a7d9c/tumblr_pg2wu1L9DM1trd056o2_500h.png",
        # "https://media.tumblr.com/701a535af224f89684d2cfcc097575ef/tumblr_pjsx70RakC1y0gqjko1_1280.pnj": "https://media.tumblr.com/701a535af224f89684d2cfcc097575ef/tumblr_pjsx70RakC1y0gqjko1_1280.pnj",

        # "https://25.media.tumblr.com/tumblr_m2dxb8aOJi1rop2v0o1_500.png": "https://25.media.tumblr.com/tumblr_m2dxb8aOJi1rop2v0o1_500.png",
        # "https://media.tumblr.com/tumblr_m2dxb8aOJi1rop2v0o1_1280.png": "https://media.tumblr.com/tumblr_m2dxb8aOJi1rop2v0o1_1280.png",
        # "https://media.tumblr.com/0DNBGJovY5j3smfeQs8nB53z_500.jpg": "https://media.tumblr.com/0DNBGJovY5j3smfeQs8nB53z_500.jpg",
        # "https://media.tumblr.com/tumblr_m24kbxqKAX1rszquso1_1280.jpg": "https://media.tumblr.com/tumblr_m24kbxqKAX1rszquso1_1280.jpg",
        # "https://va.media.tumblr.com/tumblr_pgohk0TjhS1u7mrsl.mp4": "https://va.media.tumblr.com/tumblr_pgohk0TjhS1u7mrsl.mp4",
    },
    TumblrPostUrl: {
        "https://marmaladica.tumblr.com/post/188237914346/saved": "https://marmaladica.tumblr.com/post/188237914346",
        "https://emlan.tumblr.com/post/189469423572/kuro-attempts-to-buy-a-racy-book-at-comiket-but": "https://emlan.tumblr.com/post/189469423572",
        "https://superboin.tumblr.com/post/141169066579/photoset_iframe/superboin/tumblr_o45miiAOts1u6rxu8/500/false": "https://superboin.tumblr.com/post/141169066579",
        "https://make-do5.tumblr.com/post/619663949657423872": "https://make-do5.tumblr.com/post/619663949657423872",
        "http://raspdraws.tumblr.com/image/70021467381": "https://raspdraws.tumblr.com/post/70021467381",
        "https://tumblr.com/munespice/683613396085719040": "https://munespice.tumblr.com/post/683613396085719040",
        "https://www.tumblr.com/yamujiburo/682910938493599744/will-tumblr-let-me-keep-this-up": "https://yamujiburo.tumblr.com/post/682910938493599744",
        "https://at.tumblr.com/pizza-and-ramen/118684413624/uqndb20nkyob": "https://pizza-and-ramen.tumblr.com/post/118684413624",
        "https://www.tumblr.com/blog/view/artofelaineho/187614935612": "https://artofelaineho.tumblr.com/post/187614935612",
        "https://merryweather-media.tumblr.com/post/665688699379564544/blue-eyes-white-dragon": "https://merryweather-media.tumblr.com/post/665688699379564544",
        "https://www.tumblr.com/dashboard/blog/kohirasan/136686983240": "https://kohirasan.tumblr.com/post/136686983240",
    },
    TumblrPostRedirectUrl: {
        "https://at.tumblr.com/everythingfox/everythingfox-so-sleepy/d842mqsx8lwd": "https://at.tumblr.com/everythingfox/everythingfox-so-sleepy/d842mqsx8lwd",
        "https://at.tumblr.com/cyanideqpoison/u2czj612ttzq": "https://at.tumblr.com/cyanideqpoison/u2czj612ttzq",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://www.tumblr.com/kaedech",
    url_type=TumblrArtistUrl,
    url_properties=dict(blog_name="kaedech"),
    primary_names=["????????????"],
    secondary_names=["kaedech"],
    related=[],
)
