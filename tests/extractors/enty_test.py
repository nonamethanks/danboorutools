from ward import test

from danboorutools.models.url import Url

urls = {
    "https://enty.jp/posts/141598?ref=newest_post_pc": "https://enty.jp/posts/141598",
    "https://enty.jp/en/posts/141598?ref=newest_post_pc": "https://enty.jp/posts/141598",

    "https://enty.jp/kouyoumatsunaga?active_tab=posts#2": "https://enty.jp/kouyoumatsunaga",
    "https://enty.jp/en/kouyoumatsunaga?active_tab=posts#2": "https://enty.jp/kouyoumatsunaga",
    "https://enty.jp/users/4932": "https://enty.jp/users/4932",

    # "https://img01.enty.jp/uploads/post/thumbnail/141598/post_show_b6c7d85c-b63c-4950-9152-e4bf30678022.png": "https://img01.enty.jp/uploads/post/thumbnail/141598/post_show_b6c7d85c-b63c-4950-9152-e4bf30678022.png",
    # "https://img01.enty.jp/uploads/ckeditor/pictures/194353/content_20211227_130_030_100.png": "https://img01.enty.jp/uploads/ckeditor/pictures/194353/content_20211227_130_030_100.png",

    # "https://img01.enty.jp/uploads/entertainer/wallpaper/2044/post_show_enty_top.png": "https://img01.enty.jp/uploads/entertainer/wallpaper/2044/post_show_enty_top.png",

    # "https://entyjp.s3-ap-northeast-1.amazonaws.com/uploads/post/attachment/141598/20211227_130_030_100.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIMO6YQGDXLXXJKQA%2F20221224%2Fap-northeast-1%2Fs3%2Faws4_request&X-Amz-Date=20221224T235529Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=42857026422339a2ba9ea362d91e2b34cc0718fbeee529166e8bfa80f757bb94": "https://entyjp.s3-ap-northeast-1.amazonaws.com/uploads/post/attachment/141598/20211227_130_030_100.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIMO6YQGDXLXXJKQA%2F20221224%2Fap-northeast-1%2Fs3%2Faws4_request&X-Amz-Date=20221224T235529Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=42857026422339a2ba9ea362d91e2b34cc0718fbeee529166e8bfa80f757bb94",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
