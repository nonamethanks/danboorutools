import inspect
import logging
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

        file_handler = self.add(folder / "{time}.log", retention=retention, enqueue=True, level="TRACE")

        return Path(self._core.handlers[file_handler]._sink._file.name)


logger = Logger(
    core=_Core(),
    exception=None,
    depth=0,
    record=False,
    lazy=False,
    colors=True,
    raw=False,
    capture=False,
    patcher=None,
    extra={},
)

default_level = os.environ.get("LOGURU_LEVEL") or os.environ.get("LOG_LEVEL") or "INFO"
debug = "DEBUG" if os.environ.get("DEBUG") in ["TRUE", "1"] else False
trace = "TRACE" if os.environ.get("TRACE") in ["TRUE", "1"] else False
logger_level = trace or debug or default_level

logger.add(sys.stderr, level=logger_level)


class InterceptHandler(logging.Handler):
    def emit(self, record) -> None:
        # https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


modules_to_incercept = [
    "backoff",
]

for module in modules_to_incercept:
    module_logger = logging.getLogger(module)
    module_logger.handlers = [InterceptHandler()]
