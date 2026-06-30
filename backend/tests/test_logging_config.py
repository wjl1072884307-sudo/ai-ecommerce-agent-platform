import logging

from app.core.config import Settings
from app.core.logging import configure_logging


def test_configure_logging_uses_settings_log_level():
    configure_logging(Settings(LOG_LEVEL="DEBUG"))

    assert logging.getLogger().level == logging.DEBUG
