import sys

from backend.settings.test_settings import *

CSRF_TRUSTED_ORIGINS = []
CSRF_TRUSTED_ORIGINS.extend(
    filter(
        None,
        os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(","),
    )
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}
