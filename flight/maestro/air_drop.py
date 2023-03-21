"""
File containing the functions to control dropping the bottles from the drone
"""

import maestro

BOARD: maestro.Maestro = maestro.Maestro()


def drop_bottle(bottle: int) -> None:
    """
    Drops the bottle from the drone

    Parameters
    ----------
    bottle : int
        The number of the bottle to be dropped
    """
    # I'm going to assume that we want to open the bottle by setting the servo full right
    BOARD.set_target(bottle, 8000)


def close_servo(bottle: int) -> None:
    """
    Closes the servo after bottle has been dropped

    Parameters
    ----------
    bottle : int
        The number of the bottle to be closed
    """
    BOARD.set_target(bottle, 4000)
