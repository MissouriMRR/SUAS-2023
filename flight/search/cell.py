"""
defines the Cell dataclass
"""

# pylint: disable=R0903
#NOTE: disabled the "too few public methods" error

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

    def __init__(self, probability: float, seen: bool, lat: float, lon: float, is_valid: bool):
        self.probability: float = probability
        self.seen: float = seen
        self.lat: float = lat
        self.lon: float = lon
        self.is_valid: float = is_valid
