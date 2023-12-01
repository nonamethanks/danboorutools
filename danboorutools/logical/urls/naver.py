import re
from functools import cached_property

from danboorutools.logical.sessions.naver import NaverSession
from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import extract_urls_from_string


class NaverUrl(Url):
    session = NaverSession()


class NaverBlogArtistUrl(ArtistUrl, NaverUrl):
    username: str

    normalize_template = "https://blog.naver.com/{username}"

    @property
    def primary_names(self) -> list[str]:
        widget = self.session.blog_artist_widget(self.username)
        name_el = widget.select_one("#nickNameArea")
        assert name_el
        return [name_el.text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        widget = self.session.blog_artist_widget(self.username)
        profile_caption_el = widget.select_one(".caption")
        assert profile_caption_el
        return list(map(Url.parse, extract_urls_from_string(profile_caption_el.text)))


class NaverBlogPostUrl(PostUrl, NaverUrl):
    username: str
    post_id: int

    normalize_template = "https://blog.naver.com/{username}/{post_id}"


class NaverPostArtistUrl(ArtistUrl, NaverUrl):  # fucking hell
    username: str

    normalize_template = "https://post.naver.com/{username}"


class NaverPostArtistWithIdUrl(RedirectUrl, NaverUrl):
    user_id: int

    normalize_template = "https://post.naver.com/my.nhn?memberNo={user_id}"

    @cached_property
    def resolved(self) -> NaverPostArtistUrl:
        body_scripts = self.html.select("body script[type='text/javascript']")
        match = None
        for script in body_scripts:
            if match := re.search(r'authorId : "(.*?)"', script.decode_contents()):
                break
        assert match
        assert (username := match.groups()[0])
        return NaverPostArtistUrl.build(username=username)


class NaverPostPostUrl(RedirectUrl, NaverUrl):
    user_id: int
    post_id: int

    normalize_template = "https://post.naver.com/viewer/postView.nhn?volumeNo={post_id}&memberNo={user_id}"


class NaverCafeArtistUrl(ArtistUrl, NaverUrl):
    username: str

    normalize_template = "https://cafe.naver.com/{username}"


class NaverCafeArtistWithIdUrl(RedirectUrl, NaverUrl):
    user_id: int

    normalize_template = "https://cafe.naver.com/MyCafeIntro.nhn?clubid={user_id}"

    @cached_property
    def resolved(self) -> NaverCafeArtistUrl:
        head = self.html.select_one("head")
        assert head
        match = re.search(r'var g_sCafeUrlOnly = "(.*?)";', str(head))
        assert match
        assert (username := match.groups()[0])
        return NaverCafeArtistUrl.build(username=username)


class NaverCafePostUrl(ArtistUrl, NaverUrl):
    username: str
    post_id: int

    normalize_template = "https://cafe.naver.com/{username}/{post_id}"


class NaverCafePostWithArtistIdUrl(RedirectUrl, NaverUrl):
    user_id: int
    post_id: int

    normalize_template = "https://cafe.naver.com/ca-fe/cafes/{user_id}/articles/{post_id}"

    @cached_property
    def resolved(self) -> NaverCafePostUrl:
        artist = NaverCafeArtistWithIdUrl.build(user_id=self.user_id)
        return NaverCafePostUrl.build(username=artist.resolved.username, post_id=self.post_id)


class NaverComicArtistUrl(ArtistUrl, NaverUrl):
    artist_id: int

    normalize_template = "https://comic.naver.com/artistTitle?artistId={artist_id}"


class NaverComicUrl(ArtistAlbumUrl, NaverUrl):
    comic_id: int
    comic_type: str

    normalize_template = "https://comic.naver.com/{comic_type}/list?titleId={comic_id}"


class NaverComicChapterUrl(PostUrl, NaverUrl):
    comic_id: int
    chapter_id: int
    comic_type: str

    normalize_template = "https://comic.naver.com/{comic_type}/detail?titleId={comic_id}&no={chapter_id}"


class NaverGrafolioArtistUrl(ArtistUrl, NaverUrl):
    username: str

    normalize_template = "https://grafolio.naver.com/{username}"


class NaverGrafolioPostUrl(ArtistUrl, NaverUrl):
    post_id: int

    normalize_template = "https://grafolio.naver.com/works/{post_id}"


class NaverRedirectUrl(RedirectUrl, NaverUrl):
    redirect_id: str

    normalize_template = "https://naver.me/{redirect_id}"


class NaverTvUrl(ArtistUrl, NaverUrl):
    # TODO: for related, don't associate this to the other subdomains
    username: str

    normalize_template = "https://tv.naver.com/{username}"
