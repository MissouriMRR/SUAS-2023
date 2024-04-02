"""
Testing vision.deskew.coordinate_lengths.py
"""

import json
import os.path
from typing import TypedDict
import unittest
import numpy as np

from vision.competition_inputs.bottle_reader import load_bottle_info, BottleData


class TestBottleRead(unittest.TestCase):

    "test file exists"

    def test_bottle_file(self) -> None:
        self.assertTrue(
            os.path.isfile("vision/competition_inputs/bottle.json"), "json file missing"
        )

    # self.assertEqual()
    """
    make sure bottle list has what it should in it
    """

    def test_bottle_read(self) -> None:
        with open("vision/competition_inputs/bottle.json", encoding="utf-8") as file:
            bottle_list: dict[str, BottleData] = json.load(file)
        bottle_data: dict[str, BottleData] = load_bottle_info()
        # print(bottle_data)
        # print(bottle_list)

        if set(bottle_list.keys()) == set(bottle_data.keys()):
            values_match = 1
        else:
            values_match = 0
        # Check if values are the same for corresponding keys
        if all(bottle_list[key] == bottle_data[key] for key in bottle_list.keys()):
            keys_match = 1
        else:
            keys_match = 0
        # Assert the equality
        self.assertEqual(values_match, 1)
        self.assertEqual(keys_match, 1)


if __name__ == "__main__":
    unittest.main()
