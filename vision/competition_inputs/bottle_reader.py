"""Contains things related to loading competition bottle data."""

import json

from typing import TypedDict


class BottleData(TypedDict):
    """
    BottleData sets fixed keys for the dicts found in list bottle_list.

    Attributes
    ----------
    letter : str
        The letter present on the bottle.
    letter_color : str
        The color of the letter present on the bottle.
    shape : str
        The shape surrounding the letter present on the bottle.
    shape_color : str
        The color of the shape peresent on the bottle.
    """

    letter: str
    letter_color: str
    shape: str
    shape_color: str


def load_bottle_info(
    file_path: str = "vision/competition_inputs/bottle.json",
) -> dict[str, BottleData]:
    """
    Opens and Imports bottle.json and turns it into a list of dictionaries,
    listing each bottle feature for 5 bottles with IDs '0' through '4'.

    Parameters
    ----------
    file_path : str
        Is the project location of the json file that is desired to be opened.
        By default 'vision/competition_inputs/bottle.json'.

    Returns
    -------
    bottle_list : dict[str, BottleData]
        Returns Dict of DictType BottleData containing values for 5 different bottles.
        Bottle ids are strings 0 through 4.
    """
    # Opens and imports JSON File 'Bottle.json' as a list
    with open(file_path, encoding="utf-8") as file:
        bottle_list: dict[str, BottleData] = json.load(file)

    return bottle_list


if __name__ == "__main__":
    print(load_bottle_info())
