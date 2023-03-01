from ward import test

from danboorutools.logical.artist_finder import ArtistFinder


@test("Artist name romanization", tags=["normalization"])
def _() -> None:
    name = "蜘蛛の糸"
    assert ArtistFinder.sanitize_tag_name(name) == "kumo_no_ito"
