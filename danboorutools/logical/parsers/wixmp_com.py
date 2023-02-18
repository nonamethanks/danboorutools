from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.deviantart import DeviantArtImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class KnownHosts:
    DEVIANTART = ("images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com", "wixmp-ed30a86b8c4ca887773594c2.wixmp.com")


class WixmpComParser(UrlParser):
    test_cases = {
        DeviantArtImageUrl: [
            "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/52c4a3ad-d416-42f0-90f6-570983e36797/dczr28f-bd255304-01bf-4765-8cd3-e53983d3f78a.jpg",
            "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/8b472d70-a0d6-41b5-9a66-c35687090acc/d23jbr4-8a06af02-70cb-46da-8a96-42a6ba73cdb4.jpg/v1/fill/w_786,h_1017,q_70,strp/silverhawks_quicksilver_by_edsfox_d23jbr4-pre.jpg",

            "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/76098ac8-04ab-4784-b382-88ca082ba9b1/d9x7lmk-595099de-fe8f-48e5-9841-7254f9b2ab8d.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvNzYwOThhYzgtMDRhYi00Nzg0LWIzODItODhjYTA4MmJhOWIxXC9kOXg3bG1rLTU5NTA5OWRlLWZlOGYtNDhlNS05ODQxLTcyNTRmOWIyYWI4ZC5wbmcifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.KFOVXAiF8MTlLb3oM-FlD0nnDvODmjqEhFYN5I2X5Bc",
            "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/fe7ab27f-7530-4252-99ef-2baaf81b36fd/dddf6pe-1a4a091c-768c-4395-9465-5d33899be1eb.png/v1/fill/w_800,h_1130,q_80,strp/stay_hydrated_and_in_the_shade_by_raikoart_dddf6pe-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9MTEzMCIsInBhdGgiOiJcL2ZcL2ZlN2FiMjdmLTc1MzAtNDI1Mi05OWVmLTJiYWFmODFiMzZmZFwvZGRkZjZwZS0xYTRhMDkxYy03NjhjLTQzOTUtOTQ2NS01ZDMzODk5YmUxZWIucG5nIiwid2lkdGgiOiI8PTgwMCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.J0W4k-iV6Mg8Kt_5Lr_L_JbBq4lyr7aCausWWJ_Fsbw",

            # Unparsable:
            # "https://api-da.wixmp.com/_api/download/file?downloadToken=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsImV4cCI6MTU0NDQ0NjE5NCwiaWF0IjoxNTQ0NDQ1NTg0LCJqdGkiOiI1YzBlNWU5YWQxZjk1Iiwib2JqIjpudWxsLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdLCJwYXlsb2FkIjp7InBhdGgiOiJcL2ZcLzI4OGJhMWRmLTcwNjUtNDc0NS1hMTNjLWM0Y2QwNjk2NWFhZFwvZGNwcGpyYi1mNDdhYTEwMS0yMDI5LTQxYTMtYTM2YS05ZjIxODIyM2RjMWQuanBnIn19.6vK-9PsWLgaDV7lYWOyQQbFj8fJzQazdBu_ecSvriVU",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtImageUrl | None:
        if parsable_url.hostname in KnownHosts.DEVIANTART:
            instance = DeviantArtImageUrl(parsable_url)
            instance.parse_filename(parsable_url.url_parts[-1])
            return instance
        elif parsable_url.url.startswith("https://api-da.wixmp.com/_api/download/file"):
            raise UnparsableUrl(parsable_url)

        return None
