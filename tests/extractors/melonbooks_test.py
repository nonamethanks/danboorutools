from danboorutools.logical.extractors import melonbooks as mb
from tests.extractors import generate_parsing_suite

urls = {
    mb.MelonbooksProductUrl: {
        "https://www.melonbooks.co.jp/detail/detail.php?product_id=1484137&adult_view=1": "https://www.melonbooks.co.jp/detail/detail.php?product_id=1484137",
        "https://www.melonbooks.co.jp/fromagee/detail/detail.php?product_id=1033195": "https://www.melonbooks.co.jp/detail/detail.php?product_id=1033195",
    },
    mb.MelonbooksCircleUrl: {
        "https://www.melonbooks.co.jp/circle/index.php?circle_id=107578": "https://www.melonbooks.co.jp/circle/index.php?circle_id=107578",
        "https://www.melonbooks.co.jp/fromagee/circle/index.php?circle_id=107578": "https://www.melonbooks.co.jp/circle/index.php?circle_id=107578",
        "https://www.melonbooks.co.jp/circle/?circle_id=30826": "https://www.melonbooks.co.jp/circle/index.php?circle_id=30826",
        "https://www.melonbooks.co.jp/fromagee/circle/?circle_id=32501": "https://www.melonbooks.co.jp/circle/index.php?circle_id=32501",
    },
    mb.MelonbooksAuthorUrl: {
        "https://www.melonbooks.co.jp/search/search.php?name=%E6%8A%B9%E8%8C%B6%E3%81%AD%E3%81%98&text_type=author": "https://www.melonbooks.co.jp/search/search.php?name=抹茶ねじ&text_type=author",
        "https://www.melonbooks.co.jp/search/search.php?name=%E6%98%8E%E5%9C%B0%E9%9B%AB": "https://www.melonbooks.co.jp/search/search.php?name=明地雫&text_type=author",
    },
    mb.MelonbooksCornerUrl: {
        "https://www.melonbooks.co.jp/corner/detail.php?corner_id=769": "https://www.melonbooks.co.jp/corner/detail.php?corner_id=769",
        "https://www.melonbooks.co.jp/corner/detail.php?corner_id=769#gnav": "https://www.melonbooks.co.jp/corner/detail.php?corner_id=769",
    },
    mb.MelonbooksImageUrl: {
        "https://www.melonbooks.co.jp/special/b/0/fair_dojin/20181229_touhousuiseisou2/images/itemimg5/img6_1.png": "https://www.melonbooks.co.jp/special/b/0/fair_dojin/20181229_touhousuiseisou2/images/itemimg5/img6_1.png",
        "https://www.melonbooks.co.jp/special/a/6/pb/sp/komeshiro_illust30_up.jpg": "https://www.melonbooks.co.jp/special/a/6/pb/sp/komeshiro_illust30_up.jpg",
        "https://melonbooks.akamaized.net/user_data/packages/resize_image.php?width=450&height=450&image=212001389346.jpg&c=1&aa=1": "https://www.melonbooks.co.jp/resize_image.php?image=212001389346.jpg",
        "https://www.melonbooks.co.jp/resize_image.php?image=212001389346.jpg": "https://www.melonbooks.co.jp/resize_image.php?image=212001389346.jpg",
        "http://www.melonbooks.co.jp/blogs/log/image/img08090005_1.jpg": "http://www.melonbooks.co.jp/blogs/log/image/img08090005_1.jpg",
        "https://melonbooks.akamaized.net/cplus/user_data/packages/resize_image.php?image=810000212400.jpg\u0026c=0\u0026aa=0": "https://www.melonbooks.co.jp/resize_image.php?image=810000212400.jpg",
        "https://melonbooks.akamaized.net/fromagee/user_data/packages/resize_image.php?image=216001052635.jpg\u0026c=1\u0026aa=0": "https://www.melonbooks.co.jp/resize_image.php?image=216001052635.jpg",
    },
}


generate_parsing_suite(urls)
