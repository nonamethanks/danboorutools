from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.xfolio import XfolioArtistUrl, XfolioPostUrl, XfolioUrl


class XfolioJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> XfolioUrl | None:
        match parsable_url.url_parts:
            # https://xfolio.jp/portfolio/Rei_0127/works/59931
            case "portfolio", username, "works", work_id:
                return XfolioPostUrl(parsed_url=parsable_url,
                                     username=username,
                                     post_id=int(work_id))

            # https://xfolio.jp/portfolio/hayato69/free/33407
            case "portfolio", username, "free", _:
                return XfolioArtistUrl(parsed_url=parsable_url,
                                       username=username)

            # https://xfolio.jp/portfolio/hayato69/works
            case "portfolio", username, _:
                return XfolioArtistUrl(parsed_url=parsable_url,
                                       username=username)

            # https://xfolio.jp/portfolio/hayato69
            case "portfolio", username:
                return XfolioArtistUrl(parsed_url=parsable_url,
                                       username=username)

            # https://assets.xfolio.jp/secure/1359786657/creator/8006/kv/233681_BGJnDS9ZTG.webp?hash=uRlp4fCpLOcPRcxXGBw5gw&expires=1678611600&type=main_visual&template=emotion&device=pc&pos=0
            # https://assets.xfolio.jp/secure/1359786657/creator/4227/works/59931/215274_8ZVhvrPBNn.webp?hash=89GVelCa2DOeRq-ElxxWJg&expires=1678611600
            # https://xfolio.jp/fullscale_image?image_id=543668&work_id=21562

            case _:
                return None
