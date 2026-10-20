"""Logging setup for the whole program."""

import logging


def configure_logging(
    level: int = logging.INFO, filename: str | None = "bura.log"
) -> None:
    """Send log messages to a file (or to the console if no file is given)."""

    logging.basicConfig(
        level=level,
        filename=filename,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
