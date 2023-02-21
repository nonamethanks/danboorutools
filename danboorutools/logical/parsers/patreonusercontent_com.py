from danboorutools.logical.extractors.patreon import PatreonImageUrl, PatreonUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class PatreonusercontentComParser(UrlParser):
    test_cases = {
        PatreonImageUrl: [
            "https://c10.patreonusercontent.com/4/patreon-media/p/post/78893998/a364e27cb61a42fd87f349f3380ab4cb/eyJ3Ijo2MjB9/1.jpg?token-time=1678233600&token-hash=1-9YyIHmryJw4IMnxuZuGleTLmwRNVc0jK2VY7Pq6g0%3D",
            "https://c10.patreonusercontent.com/3/eyJ3Ijo2MjB9/patreon-media/p/post/36495392/cb0702f66b4945d5adaf3fcd98d0f077/1.jpg?token-time=1591617419\u0026token-hash=C9E0pBzAiL4iKHiRhv98Otv2rXfd0ay5-hSGp6ahdZ8=",
            "https://c10.patreonusercontent.com/3/e30%3D/patreon-posts/o2-s3ubiq-rvQgJVTMlI4-_djsAXvF_YiV2LSEKkpv9sTxqhDKo9-WboTju_sjTU.png?token-time=1506470400\u0026token-hash=htqRR_7JryCMoDqgyknNFqfRWrejuahP16JKwWnaUrA%3D",
            "https://c10.patreonusercontent.com/4/patreon-media/p/post/73164326/0b437130a504407e9cddbe57b575f4d0/eyJxIjoxMDAsIndlYnAiOjB9/1.png?token-time=1668729600\u0026token-hash=cRKqb666VduPfE04ZnUQYOwkl8gWcfcJakWMrqHCUOI=",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PatreonUrl | None:
        match parsable_url.url_parts:
            case _, "patreon-media", "p", "post", post_id, *_:
                instance = PatreonImageUrl(parsable_url)
                instance.post_id = int(post_id)
            case _, _, "patreon-media", "p", "post", post_id, *_:
                instance = PatreonImageUrl(parsable_url)
                instance.post_id = int(post_id)
            case *_, "patreon-posts", _:
                instance = PatreonImageUrl(parsable_url)
            case _:
                return None

        return instance
