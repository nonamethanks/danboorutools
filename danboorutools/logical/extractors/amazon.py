from danboorutools.models.url import ArtistUrl, PostUrl, Url


class AmazonUrl(Url):
    subsite: str


class AmazonAuthorUrl(ArtistUrl, AmazonUrl):
    author_id: str

    normalize_template = "https://www.amazon.{subsite}/stores/author/{author_id}"


class AmazonItemUrl(PostUrl, AmazonUrl):
    item_id: str

    normalize_template = "https://www.amazon.{subsite}/dp/{item_id}"
