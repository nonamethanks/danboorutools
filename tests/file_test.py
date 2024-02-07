# NOTE: these tests only work on imagemagick 7.1

import pytest

from danboorutools.models.file import File, ImageFile


@pytest.mark.file
def test_transparent_png() -> None:
    f = File.identify("tests/files/transparent.png")
    assert isinstance(f, ImageFile)
    assert not f.is_animated
    assert f.md5 == "200be2be97a465ecd2054a51522f65b5"
    assert f.pixel_hash == "febaa8b547ac86ab0d11a7b24b520b64"
    assert f.short_similarity_hash == "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000111111111111000111111111111110111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"


@pytest.mark.file
def test_same_hash_1() -> None:
    f1 = File.identify("tests/files/countergirl-baseline.jpg")
    f2 = File.identify("tests/files/countergirl-progressive.jpg")
    f3 = File.identify("tests/files/countergirl-no-exif.jpg")
    # f4 = File.identify("tests/files/countergirl-rgb-gray.jpg")
    # assert len({f1.md5, f2.md5, f3.md5, f4.md5}) == 4
    assert len({f1.md5, f2.md5, f3.md5}) == 3
    assert f1.pixel_hash == f2.pixel_hash
    assert f1.pixel_hash == f3.pixel_hash
    # assert f1.pixel_hash == f4.pixel_hash


@pytest.mark.file
def test_same_hash_2() -> None:
    f1 = File.identify("tests/files/countergirl-grey.png")
    f2 = File.identify("tests/files/countergirl-grey-srgb.png")
    assert f1.md5 != f2.md5
    assert f1.pixel_hash == f2.pixel_hash


@pytest.mark.file
def test_same_hash_3() -> None:
    f1 = File.identify("tests/files/countergirl.png")
    f2 = File.identify("tests/files/countergirl-no-exif.png")
    # f3 = File.identify("tests/files/countergirl.gif")
    # assert len({f1.md5, f2.md5, f3.md5}) == 3
    assert len({f1.md5, f2.md5}) == 2
    assert f1.pixel_hash == f2.pixel_hash
    # assert f1.pixel_hash == f3.pixel_hash


@pytest.mark.file
def test_same_hash_4() -> None:
    f1 = File.identify("tests/files/countergirl-whitebg-alpha.png")
    f2 = File.identify("tests/files/countergirl-whitebg-noalpha.gif")
    f3 = File.identify("tests/files/countergirl-whitebg-noalpha.png")
    assert len({f1.md5, f2.md5, f3.md5}) == 3
    assert f1.pixel_hash == f2.pixel_hash
    assert f1.pixel_hash == f3.pixel_hash


@pytest.mark.file
def test_different_hash() -> None:
    f1 = File.identify("tests/files/countergirl-srgb.jpg")
    f2 = File.identify("tests/files/countergirl-p3.jpg")
    f3 = File.identify("tests/files/countergirl-prophoto.jpg")
    f4 = File.identify("tests/files/countergirl-adobergb.jpg")
    assert len({f1.md5, f2.md5, f3.md5, f4.md5}) == 4
    assert len({f1.pixel_hash, f2.pixel_hash, f3.pixel_hash, f4.pixel_hash}) == 4
