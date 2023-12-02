import inspect
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru._logger import Core as _Core
from loguru._logger import Logger as _Logger

load_dotenv()


class _GlobalSettings:
    _ENV_BASE_FOLDER = os.environ.get("BASE_FOLDER")
    BASE_FOLDER = Path(_ENV_BASE_FOLDER) if _ENV_BASE_FOLDER else Path(__file__).parent.parent


settings = _GlobalSettings()


class Logger(_Logger):
    def log_to_file(self,
                    folder: str | Path | None = None,
                    filename: str | Path | None = None,
                    retention: str = "7 days",
                    **kwargs) -> Path:

        if filename:
            final_path = Path(filename)
        else:
            if not folder:
                caller_path = Path(inspect.stack()[1].filename)
                folder = settings.BASE_FOLDER / "logs" / "scripts" / caller_path.stem
            final_path = Path(folder) / "{time}.log"

        file_handler = self.add(final_path, retention=retention, enqueue=True, level="TRACE", **kwargs)

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
    patchers=[],
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


# stop spam
backoff_logger = logging.getLogger("backoff")
backoff_logger.handlers = [InterceptHandler()]
logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("pyrate_limiter").setLevel(logging.INFO)
