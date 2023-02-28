import inspect
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru._logger import Core as _Core
from loguru._logger import Logger as _Logger

load_dotenv()


class Logger(_Logger):
    def log_to_file(self, folder: str | Path | None = None, retention="7 days") -> Path:
        if isinstance(folder, str):
            folder = Path(folder)
        elif not folder:
            caller_path = Path(inspect.stack()[1].filename)
            folder = Path("logs/scripts") / caller_path.stem

        file_handler = self.add(folder / "{time}.log", retention=retention, enqueue=True, level="DEBUG")

        return Path(self._core.handlers[file_handler]._sink._file.name)


logger = Logger(
    core=_Core(),
    exception=None,
    depth=0,
    record=False,
    lazy=False,
    colors=True,
    raw=False,
    capture=True,
    patcher=None,
    extra={},
)

default_level = os.environ.get("LOGURU_LEVEL") or os.environ.get("LOG_LEVEL") or "INFO"
debug = "DEBUG" if os.environ.get("DEBUG") in ["TRUE", "1"] else False
trace = "TRACE" if os.environ.get("TRACE") in ["TRUE", "1"] else False
logger_level = trace or debug or default_level

logger.add(sys.stderr, level=logger_level)
