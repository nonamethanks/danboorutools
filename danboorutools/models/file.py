import hashlib
from functools import cached_property
from pathlib import Path

import filetype

from danboorutools.util.misc import natsort_array, random_string
from danboorutools.util.system import run_external_command


class File:
    def __init__(self, raw_path: str | Path) -> None:
        if self.__class__ == File:
            raise RuntimeError("Abstract class.")
        self.raw_path = raw_path

    @classmethod
    def get_subclass_for(cls, path: Path) -> "FileSubclass":
        match path.suffix.strip("."):
            case "rar" | "zip":
                return ArchiveFile(raw_path=path)
            case _:
                return UnknownFile(raw_path=path)

    @classmethod
    def known(cls, path: Path) -> "File":
        return cls.get_subclass_for(path)

    @classmethod
    def identify(cls, path: str | Path, destination_dir: Path | None = None, md5_as_filename: bool = False) -> "FileSubclass":
        path = Path(path)
        destination_dir = destination_dir or path.parent
        destination_dir.mkdir(parents=True, exist_ok=True)

        mime_type = filetype.guess(path)
        if not mime_type:
            return UnknownFile(raw_path=path)

        _file = cls.get_subclass_for(path)

        true_ext = mime_type.extension
        true_path = path.with_suffix(f".{true_ext}")

        if md5_as_filename:
            true_path = true_path.with_stem(_file.md5)

        _file.rename(destination_dir / true_path.name)
        return cls.get_subclass_for(_file.path)

    def rename(self, target: str | Path) -> None:
        self.raw_path = Path(self.path).rename(target)

    @property
    def path(self) -> Path:
        return Path(self.raw_path).resolve()

    @cached_property
    def md5(self) -> str:
        """Return the md5 of this file."""
        hash_md5 = hashlib.md5()

        with self.path.open("rb") as myf:
            for chunk in iter(lambda: myf.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def __str__(self) -> str:
        return f"File[{self.path.name}]"
    __repr__ = __str__


class ArchiveFile(File):
    @cached_property
    def extracted_files(self) -> list[File]:
        """Extract this archive."""
        source = str(self.path)

        destination = Path("/tmp") / f"danboorutools_archive_extraction_{random_string(20)}"
        destination.mkdir(parents=True, exist_ok=True)

        run_external_command(f"aunpack {source} -X {destination}")

        subpaths = natsort_array(destination.rglob("*.*"))
        return [File.identify(subpath) for subpath in subpaths]


class UnknownFile(File):
    pass


FileSubclass = ArchiveFile | UnknownFile
