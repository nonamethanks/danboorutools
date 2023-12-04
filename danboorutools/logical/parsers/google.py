import re

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import google as g
from danboorutools.logical.urls import google_drive as gd
from danboorutools.logical.urls import google_photos as gph
from danboorutools.logical.urls import google_plus as gpl
from danboorutools.logical.urls import google_sites as gs
from danboorutools.models.url import UnsupportedUrl, Url, UselessUrl


class GoogleComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.subdomain:
            case "drive":
                return cls._match_google_drive(parsable_url=parsable_url)
            case ("forms" | "docs"):
                return UselessUrl(parsed_url=parsable_url)
            case "plus":
                return cls._match_google_plus(parsable_url=parsable_url)
            case "photos":
                return cls._match_google_photos(parsable_url=parsable_url)
            case "sites":
                return cls._match_google_site(parsable_url=parsable_url)
            case "picasaweb":
                return cls._match_picasa(parsable_url=parsable_url)
            case "profiles":
                return cls._match_google_profiles(parsable_url=parsable_url)
            case "play":
                return cls._match_google_playstore(parsable_url=parsable_url)
            case ("www" | ""):
                return cls._match_no_subdomain(parsable_url=parsable_url)
            case "calendar":
                return UselessUrl(parsed_url=parsable_url)
            # http://get.google.com/albumarchive/101812343164193175338
            case "get":
                return UnsupportedUrl(parsed_url=parsable_url)
            # https://artsandculture.google.com/entity/%2Fm%2F0p_rx
            # niggas really do be putting ancient painters on danbooru
            case "artsandculture":
                return UnsupportedUrl(parsed_url=parsable_url)
            # https://scholar.google.com/citations?hl=vi&user=gqj1QgMAAAAJ
            case "scholar":
                return UnsupportedUrl(parsed_url=parsable_url)
            case "mail":
                return UnsupportedUrl(parsed_url=parsable_url)
            case "chrome":
                return UnsupportedUrl(parsed_url=parsable_url)
            case _:
                return None

    @classmethod
    def _match_google_plus(cls, parsable_url: ParsableUrl) -> gpl.GooglePlusUrl | UnsupportedUrl | None:
        match parsable_url.url_parts:
            # https://plus.google.com/+KazuhiroMizushima/
            # http://plus.google.com/111867792020765799161
            case user_id, if cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            # https://plus.google.com/u/0/+rtil
            # http://plus.google.com/u/0/111867792020765799161
            case "u", digit, user_id if len(digit) == 1 and cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            # http://plus.google.com/u/0/114100282763774851465/posts
            # http://plus.google.com/u/0/110532977796437073008/photos
            # https://plus.google.com/u/0/101668929629889078069/about
            case "u", digit, user_id, ("posts" | "photos" | "about" | "videos") if len(digit) == 1 and cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            # http://plus.google.com/111867792020765799161/posts
            case user_id, ("posts" | "photos" | "about" | "videos") if cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            # http://plus.google.com/photos/+teracykojima/albums
            case "photos", user_id, "albums" if cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            # https://plus.google.com/u/0/b/115763191749244545325/+ilaBarattolo
            case *_, "b", user_id, username if username.startswith("+"):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=username)

            # https://plus.google.com/b/103804732399819310073/+TheWegeeMaster/posts/7F4CTCADh3u?pageId=103804732399819310073&pid=6200766528945844530&oid=103804732399819310073
            case *_, "b", user_id, username, "posts", post_id if username.startswith("+"):
                return gpl.GooglePlusPostUrl(parsed_url=parsable_url,
                                             user_id=username,
                                             post_id=post_id)

            # http://plus.google.com/photos/115260099196768427303/albums/posts
            # http://plus.google.com/photos/102433630352141229500/albums/5443277998013510145
            # http://plus.google.com/u/0/photos/+ikariyaashita/albums/6258748402112039089
            case *_, "photos", user_id, "albums", path if (path == "posts" or path.isnumeric()) and cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            # https://plus.google.com/u/0/b/115763191749244545325/102486819006366238576
            case *_, "b", user_id, _ if cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            # https://plus.google.com/photos/113088469849270210438/albums/6321484260231620177/6321484261881248162
            case "photos", user_id, ("albums" | "album"), _, _ if cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            # https://plus.google.com/104032434106102166363/posts/ipBpMGJGwvx
            case *_, user_id, "posts", post_id if cls.__validate_gplus_user_id(user_id):
                return gpl.GooglePlusPostUrl(parsed_url=parsable_url,
                                             user_id=user_id,
                                             post_id=post_id)

            case "communities", _community_id:
                return UnsupportedUrl(parsed_url=parsable_url)

            case "collection", _collection_id:
                return UnsupportedUrl(parsed_url=parsable_url)

            case _:
                return None

    @staticmethod
    def __validate_gplus_user_id(user_id: str) -> bool:
        return user_id.isnumeric() or (len(user_id) > 1 and user_id.startswith("+"))

    @staticmethod
    def _match_google_site(parsable_url: ParsableUrl) -> gs.GoogleSitesUrl | None:
        match parsable_url.url_parts:
            # http://sites.google.com/site/ondineformula/
            # https://sites.google.com/view/morionairlines/
            case ("site" | "view"), site_name:
                return gs.GoogleSitesArtistUrl(parsed_url=parsable_url,
                                               site_name=site_name)
            # https://sites.google.com/view/mustardsfm/home-page
            # http://sites.google.com/site/nonsillustgallery/tos
            # https://sites.google.com/view/darr1o/página-principal
            case ("site" | "view"), site_name, _page:
                return gs.GoogleSitesArtistUrl(parsed_url=parsable_url,
                                               site_name=site_name)

            # http://sites.google.com/site/ayakusi/_/rsrc/1304440299815/codama/touhoku-ouen2/
            case ("site" | "view"), site_name, "_", "rsrc", *post_path:
                return gs.GoogleSitesPostUrl(parsed_url=parsable_url,
                                             site_name=site_name,
                                             post_path="/".join(post_path))

            case ("site" | "view"), site_name, *_, filename if re.match(r"^.*\.(?:jpg|png|swf|gif)$", filename):
                return gs.GoogleSitesImageUrl(parsed_url=parsable_url,
                                              site_name=site_name)

            case _:
                return None

    @staticmethod
    def _match_picasa(parsable_url: ParsableUrl) -> g.GoogleUrl | UnsupportedUrl | None:
        match parsable_url.url_parts:
            # http://picasaweb.google.com/106359455091421702960
            # http://picasaweb.google.com/kinkuro1
            case username, :
                return g.GooglePicasaArtistUrl(parsed_url=parsable_url,
                                               username=username)

            case "lh", "photo", photo_id:
                return g.GooglePicasaPostUrl(parsed_url=parsable_url,
                                             photo_id=photo_id)

            case _, _:
                return UnsupportedUrl(parsed_url=parsable_url)

            case _:
                return None

    @staticmethod
    def _match_google_drive(parsable_url: ParsableUrl) -> gd.GoogleDriveUrl | None:
        match parsable_url.url_parts:
            # https://drive.google.com/drive/folders/1a3ZpLWI8NqStnH6bTmcY7d5GhnV8DiQR
            # https://drive.google.com/drive/u/0/folders/1-1toeBYF_ZJ7Jgnjf7SVxHDCKkh9L89U
            case "drive", *_, "folders", folder_id:
                return gd.GoogleDriveFolderUrl(parsed_url=parsable_url,
                                               folder_id=folder_id)

            # https://drive.google.com/drive/folders/119Rg9qtzcY2c6_zLLVKE5aNqn6wsLQkR
            case "drive", "mobile", "folders", _, folder_id:
                return gd.GoogleDriveFolderUrl(parsed_url=parsable_url,
                                               folder_id=folder_id)

            # https://drive.google.com/folderview?id=0Bz5iC3UiWJaGN2xWOERaYXotM28&usp=sharing
            case "folderview", :
                return gd.GoogleDriveFolderUrl(parsed_url=parsable_url,
                                               folder_id=parsable_url.query["id"])

            # https://drive.google.com/file/d/1zItUaRCYpJJz3Rbr0JClK24oQj4LciOP
            case "file", "d", file_id:
                return gd.GoogleDriveFileUrl(parsed_url=parsable_url,
                                             file_id=file_id)

            # https://drive.google.com/file/d/1zItUaRCYpJJz3Rbr0JClK24oQj4LciOP/view
            case "file", "d", file_id, "view":
                return gd.GoogleDriveFileUrl(parsed_url=parsable_url,
                                             file_id=file_id)

            # https://drive.google.com/open?id=1L3y8MqyDUhZlHi8FzxRzdGhIlerubnej
            case "open", :
                return gd.GoogleDriveFolderUrl(parsed_url=parsable_url,
                                               folder_id=parsable_url.query["id"])

            # https://drive.google.com/uc?export=download&id=1WpHYbFE8vNL6jzcjXbMf5sVuQKzj7dxq
            case "uc", :
                return gd.GoogleDriveFileUrl(parsed_url=parsable_url,
                                             file_id=parsable_url.query["id"])

            case _:
                return None

    @staticmethod
    def _match_google_photos(parsable_url: ParsableUrl) -> gph.GooglePhotosUrl | None:
        match parsable_url.url_parts:
            # https://photos.google.com/share/AF1QipOsY2yG-tdGQkS1hXfBECdoAgjM-DtKv1K9OHCW6UGEdsQsA0f8kmXQlG48OEeN5w?key=YTExZi1aU2ZwbXIxU3c3em9FeWRzbkhtT3NjcnNn
            case "share", folder_id, :
                return gph.GooglePhotosFolderUrl(parsed_url=parsable_url,
                                                 folder_id=folder_id,
                                                 folder_key=parsable_url.query["key"])

            # https://photos.google.com/photo/AF1QipM_y6EIrsILfA4vNSUCcH0kMbzAIXJVFYHCagl5
            case "photo", photo_id:
                return gph.GooglePhotosPhotoUrl(parsed_url=parsable_url,
                                                photo_id=photo_id)

            case _:
                return None

    @staticmethod
    def _match_google_profiles(parsable_url: ParsableUrl) -> g.GoogleProfilesUrl | None:
        match parsable_url.url_parts:
            # http://profiles.google.com/109331443954535276684/about
            case username, ("about" | "buzz" | "photos"):
                return g.GoogleProfilesUrl(parsed_url=parsable_url,
                                           username=username)

            # http://profiles.google.com/u/0/115859723697300613209
            case "u", digit, username, if len(digit) == 1:
                return g.GoogleProfilesUrl(parsed_url=parsable_url,
                                           username=username)
            case _:
                return None

    @staticmethod
    def _match_google_playstore(parsable_url: ParsableUrl) -> g.GooglePlayDeveloperUrl | UnsupportedUrl | None:
        match parsable_url.url_parts:
            # http://play.google.com/store/apps/developer?id=K2000
            case "store", "apps", "developer":
                return g.GooglePlayDeveloperUrl(parsed_url=parsable_url,
                                                developer_name=parsable_url.query["id"])
            # http://play.google.com/store/apps/dev?id=8287620048499474172
            case "store", "apps", "dev":
                return g.GooglePlayDeveloperUrl(parsed_url=parsable_url,
                                                developer_id=int(parsable_url.query["id"]))
            # https://play.google.com/store/apps/details?id=jp.co.craftegg.band
            case "store", "apps", "details":
                return UnsupportedUrl(parsed_url=parsable_url)
            case _:
                return None

    @classmethod
    def _match_no_subdomain(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # http://www.google.com/profiles/hanosukeworks
            # http://www.google.com/s2/profiles/112239079721515787480
            case *_, "profiles", username:
                return g.GoogleProfilesUrl(parsed_url=parsable_url,
                                           username=username)

            # http://google.com/+thedarkmangaka/
            case user_id, if user_id.startswith("+") and len(user_id) > 1:
                return gpl.GooglePlusArtistUrl(parsed_url=parsable_url,
                                               user_id=user_id)

            case "search", :
                return UselessUrl(parsed_url=parsable_url)

            # https://www.google.com/amp/s/making-my-fate.tumblr.com/post/180917720120/a-really-fun-commission-of-bitch-puddin-i-got/amp
            case "amp", "s", *possible_url, "amp":
                return cls.parse("https://" + "/".join(possible_url))

            # https://www.google.com/url?sa=i&url=https://centipedekun.tumblr.com/post/135798615368/the-return-of-black-haired-kaneki-in-tokyo-ghoul&psig=AOvVaw2X_GOq7hCJtlRCKugkd2Ag&ust=1632529106337000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCOC6p4irlvMCFQAAAAAdAAAAABAD
            case "url", :
                return cls.parse(parsable_url.query["url"])

            # http://www.google.com/imgres?imgurl=http://ssjserori.homestead.com/files/busty_girl.jpg&imgrefurl=http://tbzboards.proboards.com/index.cgi%3Fboard%3Dgamecube6%26action%3Dpost%26thread%3D75%26quote%3D494%26page%3D1&usg=__gPInZeXZjZ8E98Lp5zldVBfrhQY=&h=720&w=960&sz=119&hl=en&start=5&tbnid=47aqeoTc1JwYjM:&tbnh=111&tbnw=148&prev=/images%3Fq%3Dduel%2Bmasters%2Bmimi%26hl%3Den%26client%3Dsafari%26sa%3DX%26rls%3Den-us%26tbs%3Disch:1&itbs=1
            case "imgres", :
                return cls.parse(parsable_url.query["imgurl"])

            # https://www.google.com/books/edition/-KanColle-_Dengeki_Comic_Anthology:_Sasebo_Chinjufu-hen_Vol.16/0SZrtgEACAAJ
            case "books", *_:
                return UnsupportedUrl(parsed_url=parsable_url)

            case _:
                return None
