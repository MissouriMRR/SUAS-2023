"""
Benchmark for the ODLC Colors algorithm.
"""

import time

from vision.benchmarks.common.dataset import BenchImage
from vision.benchmarks.common.benchmark_base import Benchmark

from vision.common.bounding_box import BoundingBox
from vision.common.constants import Image
from vision.common.odlc_characteristics import ODLCColor

from vision.standard_object.odlc_colors import find_colors


class BenchODLCColors(Benchmark):
    """
    Benchmark utility for the ODLC Colors algorithm.

    Parameters
    ----------
    dataset : BenchDataset
        a set of images to run the benchmark on
    """

    def run_module(
        self, image: Image, text_bounds: BoundingBox | None = None
    ) -> tuple[ODLCColor, ODLCColor]:
        """
        Runs the find_colors function on the image in order to benchmark.

        Parameters
        ----------
        image : Image
            the image containing the standard odlc object
        text_bounds : BoundingBox | None, by default None
            the bounds of the text on the odlc object
            NOTE: Needs default of None to allow overriding
            of base class with different number of arguments.

        Returns
        -------
        colors : tuple[ODLCColor, ODLCColor]
            the colors of the standard object
            shape_color : ODLCColor
                the color of the shape
            text_color : ODLCColor
                the color of the text on the object
        """
        if text_bounds is None:
            raise TypeError("Required argument text_bounds not specified for run_module()")
        return find_colors(image=image, text_bounds=text_bounds)

    def accuracy(self, bench_image: BenchImage) -> list[tuple[ODLCColor, bool]]:
        """
        Run the benchmark to check accuracy of the algorithm.

        Parameters
        ----------
        bench_image : BenchImage
            the image to test the accuracy of

        Returns
        -------
        accuracy_results : list[tuple[ODLCColor, bool]]
            the accuracy results of running the algorithm on the image

            result : ODLCColor
                the color found by the algorithm
            successful : bool
                whether the algorithm's result was accurate
        """
        colors: tuple[ODLCColor, ODLCColor] = self.run_module(
            image=bench_image.image, text_bounds=bench_image.attributes["text_bounds"]
        )

        pass_color_1: bool = colors[0] == bench_image.accuracy_goals[0]
        bench_image.accuracy_results.append((colors[0], pass_color_1))

        pass_color_2: bool = colors[1] == bench_image.accuracy_goals[1]
        bench_image.accuracy_results.append((colors[1], pass_color_2))

        return bench_image.accuracy_results

    def timings(self, bench_image: BenchImage) -> list[float]:
        """
        Run the benchmark to check the timings of the algorithm.

        Parameters
        ----------
        bench_image : BenchImage
            the image to test the timeing of

        Returns
        -------
        timing_results : list[float]
            the elapsed timings of running the algorithm on the image in seconds
        """
        start_time: float = time.time()

        self.run_module(image=bench_image.image, text_bounds=bench_image.attributes["text_bounds"])

        stop_time: float = time.time()
        elapsed_time: float = start_time - stop_time

        return [elapsed_time]
