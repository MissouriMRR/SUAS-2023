"""
Base class for creating a benchmark module.
"""

import csv, time

from typing import Any

from vision.common.constants import Image
from vision.benchmarks.common.dataset import BenchImage, BenchDataset


class Benchmark:
    """
    The base class for benchmarks. Defines structure and methods
    required for benchmarks.

    Parameters
    ----------
    dataset : BenchDataset
        a set of images to run the algorithm on
    """

    def __init__(self, dataset: BenchDataset) -> None:
        self.dataset: BenchDataset = dataset

    def run_module(self, image: Image) -> Any:
        """
        Run the algorithm.

        Parameters
        ----------
        image : Image
            the image to run the algorithm on

        Returns
        -------
        result : Any
            the result of running the algorithm on the image
        """
        raise NotImplementedError(
            "Calling base Benchmark class. Function not implemented for module."
        )

    def accuracy(self, bench_image: BenchImage) -> list[tuple[Any, bool]]:
        """
        Run the benchmark to check accuracy of the algorithm.

        Parameters
        ----------
        bench_image : BenchImage
            the image to test the timing of

        Returns
        -------
        accuracy_results : list[tuple[Any, bool]]
            the accuracy results of running the algorithm on the image

            result : Any
                a result of running the algorithm
            successful : bool
                whether the result was accurate
        """
        raise NotImplementedError(
            "Calling base Benchmark class. Function not implemented for module."
        )

    def timings(self, bench_image: BenchImage) -> list[float]:
        """
        Run the benchmark to check the timings of the algorithm.

        Parameters
        ----------
        bench_image : BenchImage
            the image to test the timing of

        Returns
        -------
        timing_results : list[float]
            the timing results of running the algorithm on the image

            time : float
                the time in seconds
        """
        raise NotImplementedError(
            "Calling base Benchmark class. Function not implemented for module."
        )

    def run_all(self) -> None:
        """
        Run on all images in the dataset.
        """
        i: int
        for i in range(len(self.dataset.images)):
            bench_image: BenchImage = self.dataset.images[i]

            bench_image.accuracy_goals = self.accuracy(bench_image=bench_image)
            bench_image.timing_results = self.timings(bench_image=bench_image)

    def save_results(self) -> None:
        """
        Save the results of the benchmark to a csv file.
        """
        file_name: str = (
            self.dataset.dataset_name + "_" + str(int(time.time())) + ".csv"
        )  # name of file to save to

        with open(file_name, "w") as file:
            pass
