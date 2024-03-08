"""Definitions for the listener used for logging from seperate processes"""
import logging
from logging import handlers
from time import sleep


def listener_configurer() -> None:
    """
    The listener configurer

    This function configures the listener for logging
    """
    root = logging.getLogger()
    file_handler = handlers.RotatingFileHandler("mptest.log", "a", 30000, 10)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.setLevel(logging.DEBUG)


def listener_process(queue) -> None:  # type: ignore
    """
    The listener process

    This function configures the listener for logging

    Attributes
    ----------
    queue : Queue[Any]
        tbh I'm not really sure how to define this
    """
    listener_configurer()
    while True:
        while not queue.empty():
            record = queue.get()
            logger = logging.getLogger(record.name)
            logger.handle(record)
        sleep(1)
