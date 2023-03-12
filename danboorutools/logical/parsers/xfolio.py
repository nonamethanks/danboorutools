from danboorutools.logical.extractors.xfolio import XfolioArtistUrl, XfolioPostUrl, XfolioUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class XfolioJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> XfolioUrl | None:
        instance: XfolioUrl

        match parsable_url.url_parts:
            # https://xfolio.jp/portfolio/Rei_0127/works/59931
            case "portfolio", username, "works", work_id:
                instance = XfolioPostUrl(parsable_url)
                instance.username = username
                instance.post_id = int(work_id)

            # https://xfolio.jp/portfolio/hayato69/free/33407
            case "portfolio", username, "free", _:
                instance = XfolioArtistUrl(parsable_url)
                instance.username = username

            # https://xfolio.jp/portfolio/hayato69/works
            case "portfolio", username, _:
                instance = XfolioArtistUrl(parsable_url)
                instance.username = username

            # https://xfolio.jp/portfolio/hayato69
            case "portfolio", username:
                instance = XfolioArtistUrl(parsable_url)
                instance.username = username

            # https://assets.xfolio.jp/secure/1359786657/creator/8006/kv/233681_BGJnDS9ZTG.webp?hash=uRlp4fCpLOcPRcxXGBw5gw&expires=1678611600&type=main_visual&template=emotion&device=pc&pos=0
            # https://assets.xfolio.jp/secure/1359786657/creator/4227/works/59931/215274_8ZVhvrPBNn.webp?hash=89GVelCa2DOeRq-ElxxWJg&expires=1678611600
            # https://xfolio.jp/fullscale_image?image_id=543668&work_id=21562

            case _:
                return None

        return instance
