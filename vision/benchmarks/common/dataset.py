"""
Dataset classes.
"""

import csv

from typing import Any

import cv2

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

        # any other attributes needed for running the benchmark on the image
        self.attributes: dict[str, Any] = {}

        # result of accuracy run, a pair of output and whether it was an accurate result
        self.accuracy_results: list[tuple[Any, bool]] = []

        # result of timing run, in seconds
        self.timing_results: list[float]
    
    def set_attribute(self, attribute_name: str, attribute: Any) -> None:
        """
        Sets an attribute of the image.

        Parameters
        ----------
        attribute_name : str
            the name of the attribute
        attribute : Any
            the value to set the attribute to, which can be of any type
        """
        self.attributes[attribute_name] = attribute

    def get_attribute(self, attribute_name: str) -> Any:
        """
        Gets an attribute of the image.

        Parameters
        ----------
        attribute_name : str
            the name of the attribute

        Returns
        -------
        attribute : Any
            the value of the attribute, which can be of any type
        """
        return self.attributes[attribute_name]


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


def load_dataset(filename: str, dataset_name: str) -> BenchDataset:
    """
    Load a dataset from a csv file.

    NOTE: csv file is formatted as follows, with the first line being the headings
        image_name, goal1, goal2, ...

    Parameters
    ----------
    filename : str
        the path and name of the file

    Returns
    -------
    BenchDataset
        the resulting dataset
    """
    images: list[BenchImage] = []
    headings: list[str] = []

    # load images from file
    with open(filename, mode="r") as file:
        csv_file = csv.reader(file)

        for i, line in enumerate(csv_file):
            if i == 0:  # headings
                headings = line
            else:  # data
                image_name = line[0]
                image: Image = cv2.imread(image_name)  # load the image
                accuracy_goals: list[Any] = line[1:]  # the rest of the line is goals

                # create the benchmark image and add to list
                bench_image: BenchImage = BenchImage(
                    image=image, image_name=image_name, accuracy_goals=accuracy_goals
                )
                images.append(bench_image)

    # create and return the dataset
    dataset: BenchDataset = BenchDataset(
        images=images, headings=headings, dataset_name=dataset_name
    )
    return dataset
