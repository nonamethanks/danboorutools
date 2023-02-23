from danboorutools.models.url import PostUrl


class StaShUrl(PostUrl):
    normalization = "https://sta.sh/{stash_id}"

    stash_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        stash_id = kwargs["stash_id"]
        return f"https://sta.sh/{stash_id}"
