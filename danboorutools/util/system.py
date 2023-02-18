import subprocess
from pathlib import Path
from threading import Lock
from typing import Generic, TypeVar


def run_external_command(command: str) -> subprocess.CompletedProcess:
    """Run a subprocess command safely and return the output as a string."""
    try:
        output = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        printable_output = e.output.decode(errors="backslashreplace")
        raise RuntimeError(f"Command '{e.cmd}' exited with error (code {e.returncode}): {printable_output}") from e
    return output


PersistentValueVal = TypeVar("PersistentValueVal")


class PersistentValue(Generic[PersistentValueVal]):
    def __init__(self, name: str, default_value: PersistentValueVal) -> None:
        self.name = name
        self.file = Path(f"data/progress/{name}")
        self.file.parent.mkdir(parents=True, exist_ok=True)

        self.value_type = type(default_value)
        self._value_lock = Lock()

        with self._value_lock:
            if not self.file.exists():
                self._value = default_value
            else:
                raw_value = self.file.read_text(encoding="utf-8")
                self._value = self.value_type(raw_value)  # type: ignore[call-arg]

    @property
    def value(self) -> PersistentValueVal:
        with self._value_lock:
            return self._value

    @value.setter
    def value(self, new_value: PersistentValueVal) -> None:
        with self._value_lock:
            self.file.write_text(str(new_value), encoding="utf-8")
        self._value = new_value

    def delete(self) -> None:
        with self._value_lock:
            self.file.unlink(missing_ok=True)

        del self._value
