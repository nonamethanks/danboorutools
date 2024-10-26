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
    def log_to_file(self,  # noqa: PLR0913
                    *,
                    filename: str | Path | None = None,
                    folder: str | Path | None = None,
                    retention: str | int = "7 days",
                    level: str = "TRACE",
                    precise_file_path: str | Path | None = None,
                    **kwargs) -> Path:
        caller_path = Path(inspect.stack()[1].filename)

        skip_first_print = False
        if precise_file_path:
            final_path = Path(precise_file_path)
            if final_path.exists():
                skip_first_print = True
        else:
            if filename:  # noqa: SIM108
                filename = Path(filename).stem + "_{time}.log"
            else:
                filename = Path(inspect.stack()[1].filename).name + "_{time}.log"

            folder = Path(folder) if folder else settings.BASE_FOLDER / "logs" / "scripts" / caller_path.stem
            final_path = Path(folder) / filename

        file_handler = self.add(final_path, retention=retention, enqueue=True, level=level, **kwargs)

        log_path = Path(self._core.handlers[file_handler]._sink._file.name)

        if not skip_first_print:
            logger.trace(f"Started logging at {log_path}.")

        return log_path


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

logger.add(
    sys.stderr,
    level=logger_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | <level>{message}</level>",
)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# stop spam
backoff_logger = logging.getLogger("backoff")
backoff_logger.handlers = [InterceptHandler()]
logging.getLogger("pyrate_limiter").setLevel(logging.INFO)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.INFO)
