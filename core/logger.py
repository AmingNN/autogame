import logging
import logging.config
import logging.handlers
from datetime import datetime
from core.common import cfg


cfg.log_dir.mkdir(parents=True, exist_ok=True)
log_file = cfg.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": str(log_file),
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        # 自定义主日志：输出到控制台 + 文件
        "AutoGame": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        # 以下第三方 logger 仅保留 WARNING 以上，且不传播到根 logger
        "uvicorn": {"level": "WARNING", "handlers": ["file"], "propagate": False},
        "uvicorn.error": {"level": "WARNING", "handlers": ["file"], "propagate": False},
        "uvicorn.access": {"level": "WARNING", "handlers": [], "propagate": False},
        "fastapi": {"level": "WARNING", "handlers": [], "propagate": False},
        "urllib3": {"level": "WARNING", "handlers": [], "propagate": False},
        "httpcore": {"level": "WARNING", "handlers": [], "propagate": False},
        "httpx": {"level": "WARNING", "handlers": [], "propagate": False},
        "requests": {"level": "WARNING", "handlers": [], "propagate": False},
        # 项目内部子模块 logger：跟随 AutoGame，输出到控制台 + 文件
        "skyland": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
        # 根 logger：静默（警告以上才写文件，不打印控制台）
        "": {
            "handlers": ["file"],
            "level": "WARNING",
        },
    },
}


def _log_header(log: logging.Logger) -> None:
    width = 40
    log.info("=" * width)
    log.info(f"{'Auto Game Report':^{width}}")
    log.info(f"{'RUNNING':^{width}}")
    log.info("=" * width)


def init_app_logging() -> logging.Logger:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("AutoGame")
    _log_header(logger)
    return logger


mlog: logging.Logger = init_app_logging()
