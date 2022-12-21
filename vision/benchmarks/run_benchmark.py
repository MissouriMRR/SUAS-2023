"""
Run a vision benchmark for timings and accuracy.
"""

# Driver for running a vision benchmark
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Must specify benchmark name and location of files to run on."
    )
