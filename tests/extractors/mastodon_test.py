from danboorutools.logical.extractors import mastodon as m
from tests.extractors import assert_artist_url, assert_info_url, generate_parsing_suite

urls = {


}

urls = {
    m.MastodonArtistUrl: {
        "https://pawoo.net/@evazion": "https://pawoo.net/@evazion",
        "https://baraag.net/@danbooru": "https://baraag.net/@danbooru",
        "https://baraag.net/@quietvice/media": "https://baraag.net/@quietvice",
        "https://baraag.net/web/@loodncrood": "https://baraag.net/@loodncrood",
        "https://pawoo.net/users/esoraneko": "https://pawoo.net/@esoraneko",
        "https://pawoo.net/users/khurata/media": "https://pawoo.net/@khurata",
    },
    m.MastodonWebIdUrl: {
        "https://pawoo.net/web/accounts/47806": "https://pawoo.net/web/accounts/47806",
        "https://baraag.net/web/accounts/107862785324786980": "https://baraag.net/web/accounts/107862785324786980",
    },
    m.MastodonPostUrl: {
        "https://pawoo.net/@evazion/19451018": "https://pawoo.net/@evazion/19451018",
        "https://baraag.net/@curator/102270656480174153": "https://baraag.net/@curator/102270656480174153",
        "https://pawoo.net/web/statuses/19451018": "https://pawoo.net/web/statuses/19451018",
        "https://pawoo.net/web/statuses/19451018/favorites": "https://pawoo.net/web/statuses/19451018",
        "https://baraag.net/web/statuses/102270656480174153": "https://baraag.net/web/statuses/102270656480174153",
    },
    m.MastodonImageUrl: {
        "https://img.pawoo.net/media_attachments/files/001/297/997/small/c4272a09570757c2.png": "https://img.pawoo.net/media_attachments/files/001/297/997/original/c4272a09570757c2.png",
        "https://img.pawoo.net/media_attachments/files/001/297/997/original/c4272a09570757c2.png": "https://img.pawoo.net/media_attachments/files/001/297/997/original/c4272a09570757c2.png",
        "https://baraag.net/system/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4": "https://baraag.net/system/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4",
        "https://media.baraag.net/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4": "https://media.baraag.net/media_attachments/files/107/866/084/749/942/932/original/a9e0f553e332f303.mp4",

    },
    m.MastodonOldImageUrl: {
        "https://pawoo.net/media/lU2uV7C1MMQSb1czwvg": "https://pawoo.net/media/lU2uV7C1MMQSb1czwvg",
    },
    m.MastodonOauthUrl: {
        "https://pawoo.net/oauth_authentications/25289748": "https://pawoo.net/oauth_authentications/25289748",
    }
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://pawoo.net/@2075642",
    url_type=m.MastodonArtistUrl,
    url_properties=dict(username="2075642"),
    primary_names=["はいむら"],
    secondary_names=["2075642"],
    related=["http://r-s.sakura.ne.jp/", "https://twitter.com/haimurakiyotaka"],
)

assert_info_url(
    "https://pawoo.net/web/accounts/457571",
    url_type=m.MastodonWebIdUrl,
    url_properties=dict(user_id=457571),
    primary_names=["はいむら"],
    secondary_names=["2075642"],
    related=["http://r-s.sakura.ne.jp", "https://twitter.com/haimurakiyotaka",
             "https://pawoo.net/@2075642", "https://www.pixiv.net/en/users/164728"],
)
