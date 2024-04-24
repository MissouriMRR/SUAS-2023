"""Functions and Configurations for logging flight & vision data during flight"""

from __future__ import annotations

import logging

from typing import TextIO
from multiprocessing import Queue
from logging import Formatter, FileHandler, StreamHandler
from logging.handlers import QueueHandler, QueueListener
from datetime import datetime

from colorlog import ColoredFormatter

LOG_FILE: str = f"logs/{datetime.now()}.log"
LOG_LEVEL = logging.DEBUG
LOG_FORMAT: str = "%(levelname)s | %(asctime)s @ %(processName)s:%(funcName)s > %(message)s"
COLOR_LOG_FORMAT: str = (
    "%(log_color)s%(levelname)s | %(asctime)s @ "
    + " %(processName)s:%(funcName)s > %(message)s%(reset)s"
)


def init_logger(queue: Queue[str]) -> QueueListener:
    """
    Initializes a QueueListener object to be used throughout the competition
    code to contain log messages

    Parameters
    ----------
    queue : Queue[str]
        Data structure to hold logging messages

    Returns
    -------
    queue_listener : QueueListener
        Object to process log messages
    """

    file_formatter: Formatter = logging.Formatter(LOG_FORMAT)
    file: FileHandler = logging.FileHandler(LOG_FILE)
    file.setFormatter(file_formatter)

    console_formatter: Formatter = ColoredFormatter(COLOR_LOG_FORMAT)
    console: StreamHandler[TextIO] = logging.StreamHandler()
    console.setFormatter(console_formatter)

    return QueueListener(queue, file, console)


def worker_configurer(queue: Queue[str]) -> None:
    """
    Configures the logger to send logging messages to QueueListener process

    Parameters
    ----------
    queue : Queue[str]
        Data structure that holds logging messages
    """
    queue_handler: QueueHandler = QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(queue_handler)
    root.setLevel(LOG_LEVEL)
