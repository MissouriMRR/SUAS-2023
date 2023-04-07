"""
Run a vision benchmark for timings and accuracy.
"""

import os

from enum import Enum

from vision.benchmarks.common.benchmark_base import Benchmark
from vision.benchmarks.common.dataset import BenchDataset, load_dataset

from vision.benchmarks.modules.bench_odlc_colors import BenchODLCColors
from vision.benchmarks.modules.bench_odlc_image_processing import BenchODLCImageProcessing


class ValidBenchmarks(str, Enum):
    """
    An enumeration of all valid/implemented benchmarks that can be run.
    """

    ODLC_COLORS = "ODLC Colors"
    ODLC_IMAGE_PROCESSING = "ODLC Image Processing"


# Driver for running a vision benchmark
if __name__ == "__main__":
    import argparse

    # handle command line arguments
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Must specify benchmark name, location of csv file, and the benchmark to run."
    )
    parser.add_argument(
        "-f",
        "--file_location",
        type=str,
        help="Location of the csv file that specifies the benchmark dataset. Required Argument.",
    )
    parser.add_argument(
        "-n", "--dataset_name", type=str, help="Name of the dataset. Required Argument."
    )
    parser.add_argument(
        "-b",
        "--benchmark",
        type=str,
        help="The benchmark to run. Must be valid benchmark. Required Argument.",
    )

    args: argparse.Namespace = parser.parse_args()

    # handle required arguments
    if not args.file_location:
        raise RuntimeError("No csv file specified.")
    file_location: str = args.file_location

    if not args.dataset_name:
        raise RuntimeError("No dataset name specified.")
    dataset_name: str = args.dataset_name

    if not args.benchmark:
        raise RuntimeError("No benchmark specified.")
    benchmark_type: ValidBenchmarks = ValidBenchmarks()

    # parse the csv dataset
    if not os.path.exists(file_location):
        raise RuntimeError("Specified CSV file does not exist.")
    dataset: BenchDataset = load_dataset(filename=file_location, dataset_name=dataset_name)

    # parse benchmark to run
    benchmark: Benchmark | None = None
    if benchmark_type == ValidBenchmarks.ODLC_COLORS:
        benchmark = BenchODLCColors(dataset=dataset)
    elif benchmark_type == ValidBenchmarks.ODLC_IMAGE_PROCESSING:
        benchmark = BenchODLCImageProcessing(dataset=dataset)
    else:
        raise RuntimeError("Invalid Benchmark")
