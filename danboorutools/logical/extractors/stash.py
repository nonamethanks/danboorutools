from danboorutools.models.url import PostUrl


class StaShUrl(PostUrl):
    normalization = "https://sta.sh/{stash_id}"

    stash_id: str

    normalize_string = "https://sta.sh/{stash_id}"
