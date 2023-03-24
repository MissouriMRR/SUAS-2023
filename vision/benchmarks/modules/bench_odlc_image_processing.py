"""
Benchmark for the ODLC Image Processing algorithm.
"""

import time

from vision.benchmarks.common.dataset import BenchImage
from vision.benchmarks.common.benchmark_base import Benchmark

from vision.common.constants import Image

from vision.standard_object.odlc_image_processing import preprocess_std_odlc


class BenchODLCImageProcessing(Benchmark):
    """
    Benchmark utility for the ODLC image processing algorithm.

    Parameters
    ----------
    dataset : BenchDataset
        a set of images to run the benchmark on
    """

    def run_module(self, image: Image) -> Image:
        """
        Runs the preprocess_std_odlc function on the image in order to benchmark.

        Parameters
        ----------
        image : Image
            the image of part of the air drop area

        Returns
        -------
        dilated : Image
            the preprocessed image
        """
        return preprocess_std_odlc(image=image)

    def accuracy(self, bench_image: BenchImage) -> list[tuple[None, bool]]:
        """
        Run the benchmark to check accuracy of the algorithm.

        Parameters
        ----------
        bench_image : BenchImage
            the image to test the accuracy of

        Returns
        -------
        accuracy_results : list[tuple[None, bool]]
            the accuracy results of running the algorithm on the image

            None : None
                placeholder, no accurracy tested
            successful : bool
                whether the algorithm's result was accurate
        """
        self.run_module(image=bench_image.image)

        bench_image.accuracy_results.append((None, True))

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

        self.run_module(image=bench_image.image)

        stop_time: float = time.time()
        elapsed_time: float = start_time - stop_time

        return [elapsed_time]
