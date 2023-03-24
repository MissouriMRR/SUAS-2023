"""
Base class for creating a benchmark module.
"""

import csv
import time

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
        a set of images to run the benchmark on
    """

    def __init__(self, dataset: BenchDataset) -> None:
        self.dataset: BenchDataset = dataset

    def run_module(self, image: Image) -> Any | Exception:
        """
        Run the algorithm to be benchmarked.

        NOTE: When adding additional parameters in inheriting
        classes, new parameters should default to None to continue
        overwritting this function.

        Parameters
        ----------
        image : Image
            the image to run the algorithm on

        Returns
        -------
        result : Any | Exception
            the result of running the algorithm on the image, or
            an exception if one occurred
        """
        raise NotImplementedError(
            "Calling base Benchmark class. Function not implemented for module."
        )

    def accuracy(self, bench_image: BenchImage) -> list[tuple[Any, bool]]:
        """
        Run the benchmark to check accuracy of the algorithm.

        NOTE: When adding additional parameters in inheriting
        classes, new parameters should default to None to continue
        overwritting this function.

        Parameters
        ----------
        bench_image : BenchImage
            the image to test the accuracy of

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

        NOTE: When adding additional parameters in inheriting
        classes, new parameters should default to None to continue
        overwritting this function.

        Parameters
        ----------
        bench_image : BenchImage
            the image to test the timing of

        Returns
        -------
        timing_results : list[float]
            the elapsed timings of running the algorithm on the image in seconds
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

        with open(file_name, "w", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)

            csv_writer.writerow(self.dataset.headings)

            img_results: BenchImage
            for img_results in self.dataset.images:
                row: list[Any] = [img_results.image_name]

                acc_result: tuple[Any, bool]
                for acc_result in img_results.accuracy_results:
                    row.append(str(acc_result[0]) + "(Success=" + str(acc_result[1]) + ")")

                time_result: float
                for time_result in img_results.timing_results:
                    row.append(time_result)

                csv_writer.writerow(row)

    def print_error(self, error: Exception, bench_image: BenchImage) -> None:
        """
        Prints an error that occurred when running a module

        Parameters
        ----------
        error : Excpetion
            the error that occurred
        bench_image : BenchImage
            the image that the module failed on
        """
        print(
            "An error occurred when running",
            str(self.__class__),
            "on",
            bench_image.image_name,
            ". Error:\n",
            str(error),
        )
