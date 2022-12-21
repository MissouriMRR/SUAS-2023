"""
Base class for creating a benchmark module.
"""


class Benchmark:
    """
    The base class for benchmarks. Defines structure and methods
    required for benchmarks.
    """

    def __init__(self) -> None:
        pass

    def run_module(self) -> None:
        """
        Run the algorithm.
        """
        raise NotImplementedError(
            "Calling base Benchmark class. Function not implemented for module."
        )

    def accuracy() -> None:
        """
        Run the benchmark to check accuracy of the algorithm.
        """
        raise NotImplementedError(
            "Calling base Benchmark class. Function not implemented for module."
        )

    def timings() -> None:
        """
        Run the benchmark to check the timings of the algorithm.
        """
        raise NotImplementedError(
            "Calling base Benchmark class. Function not implemented for module."
        )

    def run_all() -> None:
        """
        Run on all images in the dataset.
        """
        pass
