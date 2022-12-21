"""
Dataset classes.
"""

from typing import Any

from vision.constants import Image


class BenchImage:
    """
    An image along with its accuracy and timing information

    Parameters
    ----------
    image : Image
        the image to run a benchmark on
    image_name : str
        the name of the image
    accuracy_goals : list[Any]
        desired result from running an accuracy benchmark
    """

    def __init__(self, image: Image, image_name: str, accuracy_goals: list[Any]) -> None:
        self.image: Image = image
        self.image_name: str = image_name
        self.accuracy_goals: list[Any] = accuracy_goals

        # result of accuracy run, a pair of output and whether it was an accurate result
        self.accuracy_results: list[tuple[Any, bool]] = []

        # result of timing run, in seconds
        self.timing_results: list[float]
