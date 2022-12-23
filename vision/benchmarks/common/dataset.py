"""
Dataset classes.
"""

from typing import Any

from vision.common.constants import Image


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


class BenchDataset:
    """
    A set of BenchImages to run a benchmark on.

    Parameters
    ----------
    images : list[BenchImage]
        a set of images to run a benchmark on

        image : BenchImage
            an image for running a benchmark on
    headings : list[str]
        the headings for benchmark results

        heading : str
            a heading for the resulting csv file
    set_name : str
        the name of the dataset
    """

    def __init__(self, images: list[BenchImage], headings: list[str], dataset_name: str) -> None:
        self.images: list[BenchImage] = images
        self.headings: list[str] = headings
        self.dataset_name: str = dataset_name
