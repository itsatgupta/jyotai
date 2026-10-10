"""Runtime logging setup for JyotishAI application diagnostics."""

import logging

_APPLICATION_LOGGER_NAME = "astrologer"


def configure_application_logging() -> None:
    """Make safe JyotishAI INFO diagnostics visible with Uvicorn's default config.

    Uvicorn configures its own loggers but leaves the root logger at WARNING and
    without a handler.  Application loggers therefore inherit WARNING unless we
    explicitly opt the application namespace into INFO and provide a root sink.
    Parent logger levels do not filter propagated records; the root handler uses
    NOTSET so it accepts the application's INFO records.
    """
    logging.getLogger(_APPLICATION_LOGGER_NAME).setLevel(logging.INFO)
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    root_logger.addHandler(handler)
