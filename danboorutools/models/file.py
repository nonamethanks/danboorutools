from __future__ import annotations

import hashlib
import shutil
import tempfile
from functools import cached_property
from pathlib import Path

import filetype
import imagehash
import ring
from PIL import Image

from danboorutools.util.misc import natsort_array, random_string
from danboorutools.util.system import run_external_command


class File:
    def __init__(self, raw_path: str | Path) -> None:
        if self.__class__ == File:
            raise RuntimeError("Abstract class.")
        self.raw_path = raw_path

    def __str__(self) -> str:
        return f"File[{self.path.name}]"
    __repr__ = __str__

    @classmethod
    def get_subclass_for(cls, path: Path) -> FileSubclass:
        match path.suffix.strip("."):
            case "rar" | "zip":
                return ArchiveFile(raw_path=path)
            case "jpg" | "png":
                return ImageFile(raw_path=path)
            case _:
                return UnknownFile(raw_path=path)

    @classmethod
    def known(cls, path: Path) -> File:
        return cls.get_subclass_for(path)

    @classmethod
    def identify(cls, path: str | Path, destination_dir: Path | None = None, md5_as_filename: bool = False) -> FileSubclass:
        path = Path(path)
        destination_dir = destination_dir or path.parent
        destination_dir.mkdir(parents=True, exist_ok=True)

        mime_type = filetype.guess(path)

        if not mime_type:
            final_path = path
        else:
            true_ext = mime_type.extension
            final_path = path.with_suffix(f".{true_ext}")

        _file = cls.get_subclass_for(path)
        if md5_as_filename:
            final_path = final_path.with_stem(_file.md5)

        _file.rename(destination_dir / final_path.name)
        return cls.get_subclass_for(_file.path)

    def rename(self, target: str | Path) -> None:
        self.raw_path = Path(shutil.move(self.path, target))

    @property
    def path(self) -> Path:
        return Path(self.raw_path).resolve()

    @cached_property
    def md5(self) -> str:
        """Return the md5 of this file."""
        hash_md5 = hashlib.md5(usedforsecurity=False)

        with self.path.open("rb") as myf:
            for chunk in iter(lambda: myf.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def delete(self) -> None:
        self.path.unlink()

    @property
    def file_size(self) -> int:
        return self.path.stat().st_size


class ArchiveFile(File):
    @cached_property
    def extracted_files(self) -> list[File]:
        """Extract this archive."""
        source = str(self.path)

        destination = Path(tempfile.gettempdir()) / f"danboorutools_archive_extraction_{random_string(20)}"
        destination.mkdir(parents=True, exist_ok=True)

        run_external_command(f"aunpack {source} -X {destination}")

        subpaths = natsort_array(destination.rglob("*.*"))
        return [File.identify(subpath) for subpath in subpaths]


class ImageFile(File):
    @cached_property
    def sizes(self) -> tuple[int, int]:
        """Return the width and height of this file."""
        with Image.open(self.path) as img:
            return img.size

    @cached_property
    def width(self) -> int:
        """Return the width of this file."""
        return self.sizes[0]

    @cached_property
    def height(self) -> int:
        """Return the height of this file."""
        return self.sizes[1]

    @cached_property
    def short_similarity_hash(self) -> str:
        """Return a short wavelet hash (256 char) for this image."""
        return self._get_whash(16)

    @cached_property
    def long_similarity_hash(self) -> str:
        """Return a long wavelet hash (16384 char) for this image."""
        return self._get_whash(128)

    @ring.lru()
    def _get_whash(self, size: int) -> str:
        with Image.open(self.path) as img:
            string_hash = str(imagehash.whash(img, size))

        return bin(int(string_hash, 16))[2:].zfill(size**2)

    @ring.lru()
    def hamming_distance(self, other_file: ImageFile) -> int:
        own_hash = self.long_similarity_hash
        other_hash = other_file.long_similarity_hash

        return sum(c1 != c2 for c1, c2 in zip(own_hash, other_hash, strict=True))

    def thumbnail(self, max_w: int = 100, max_h: int = 100, quality: int = 90, final_dir: str | Path = "/tmp") -> Path:  # noqa: S108
        thumb_path = Path(final_dir) / f"{self.md5}_thumb.jpg"
        with Image.open(self.path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")  # noqa: PLW2901
            img.thumbnail((max_w, max_h))
            img.save(thumb_path, quality=quality, optimize=True)

        return thumb_path


class UnknownFile(File):
    pass


FileSubclass = ArchiveFile | UnknownFile
