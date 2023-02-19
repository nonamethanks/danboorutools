from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.bilibili import BilibiliImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class HdslbComParser(UrlParser):
    test_cases = {
        BilibiliImageUrl: [
            "https://i0.hdslb.com/bfs/new_dyn/675526fd8baa2f75d7ea0e7ea957bc0811742550.jpg@1036w.webp",
            "https://i0.hdslb.com/bfs/new_dyn/716a9733fc804d11d823cfacb7a3c78b11742550.jpg@208w_208h_1e_1c.webp",

            "https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif@1036w.webp",
            "https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif",
            "https://i0.hdslb.com/bfs/article/48e75b3871fa5ed62b4e3a16bf60f52f96b1b3b1.jpg@942w_1334h_progressive.webp",

            "https://i0.hdslb.com/bfs/activity-plat/static/2cf2b9af5d3c5781d611d6e36f405144/E738vcDvd3.png",
            "https://i0.hdslb.com/bfs/new_dyn/bb4e6e265174f53672ba9c87fcf23f0f468367.jpg",  # TODO: fix this on danbooru code too: not 8 digits
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BilibiliImageUrl | None:
        match parsable_url.url_parts:

            # https://i0.hdslb.com/bfs/new_dyn/675526fd8baa2f75d7ea0e7ea957bc0811742550.jpg@1036w.webp
            # https://i0.hdslb.com/bfs/new_dyn/716a9733fc804d11d823cfacb7a3c78b11742550.jpg@208w_208h_1e_1c.webp
            case "bfs", "new_dyn", filename:
                instance = BilibiliImageUrl(parsable_url)
                instance.user_id = int(filename.split(".")[0][32:])

            # https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif@1036w.webp
            # https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif
            # https://i0.hdslb.com/bfs/article/48e75b3871fa5ed62b4e3a16bf60f52f96b1b3b1.jpg@942w_1334h_progressive.webp
            case "bfs", ("album" | "article"), _:
                instance = BilibiliImageUrl(parsable_url)
                instance.user_id = None

            # https://i0.hdslb.com/bfs/activity-plat/static/2cf2b9af5d3c5781d611d6e36f405144/E738vcDvd3.png
            case "bfs", "activity-plat", _, _, _:
                raise UnparsableUrl(parsable_url)  # 404 images I think?

            # https://i0.hdslb.com/u_user/879a1e5ac43748c4c27ccbb2cb3497f7.png
            # http://i0.hdslb.com/Wallpaper/summer_2011_wide.jpg
            # http://i1.hdslb.com/u_user/Wallpaper/bilibili_5th.png
            case *_, ("u_user" | "Wallpaper"), _:
                raise UnparsableUrl(parsable_url)  # 404 images I think?

            case _:
                return None

        return instance
