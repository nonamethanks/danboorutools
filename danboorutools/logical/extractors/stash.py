from danboorutools.models.url import PostUrl


class StaShUrl(PostUrl):
    stash_id: str
    normalize_string = "https://sta.sh/{stash_id}"   # "https://sta.sh/zip/{stash_id}", <- download url
