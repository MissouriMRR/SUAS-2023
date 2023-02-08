"""
defines the Cell dataclass
"""

from dataclasses import dataclass


@dataclass
class Cell:
    """
    Represents a grid cell in the search area.

    Attributes
    ----------
    probability : float
        The initial probability of the cell containing an ODLC. Often will be
        ODLCs / num_cells_in_grid.
    seen : bool
        Represents whether the drone has seen the cell. Initially False.
    lat : float
        The cell's latitude
    lon : float
        The Cell's longitude
    is_valid : bool
        Represents whether the cell is actually within the ODLC search area.
    """

    probability: float
    seen: bool
    lat: float
    lon: float
    is_valid: bool
