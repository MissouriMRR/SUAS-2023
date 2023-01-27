"""
Defines the CellMap class and has some basic tests at the bottom of the file.
"""
#pylint: disable=C0200
from flight.search.cell import Cell
from flight.search.helper import get_bounds


class CellMap:
    """
    a two-dimensional array where the row element's are square segments of the
    search area, each associated with some probability of having an ODLC

    Attributes
    ----------
    data : list[list[Cell]
        a two-dimensional array of Cell objects that defines
        the search area
    num_valids : int
        the number of Cells within the bounds,
    bounds: dict[str, list[float]]
        the latitude longitude boundaries of the search area

    Methods
    -------
    __get_valids(points: list[list[tuple[float, float] | str]]) -> int
        returns the number of valid points in the points passed to the CellMap
    __init_map(points: list[list[tuple[float, float] | str]], odlc_count: int)-> list[list[Cell]]
        creates two-dimensional list of Cells
    display()
        prints state of CellMap into standard output
    """
    def __init__(self, points: list[list[tuple[float, float] | str]], odlc_count: int = 1) -> None:
        """
        initializes the object with given parameters

        Parameters
        ----------
        points : list[list[tuple[float, float] | str]]
            a collection of latitude, longitude coordinates to define the map
        odlc_count : int
            the number of ODLCs in the flight area
        """
        self.num_valids: int = self.__get_valids(points)
        self.data: list[list[Cell]] = self.__init_map(points, odlc_count)

        flat_list: list[tuple[float, float]] = []
        sublist: list[Cell]
        for sublist in self.data:
            item: Cell
            for item in sublist:
                if item.is_valid:
                    flat_list.append((item.lat, item.lon))
        self.bounds: dict[str, list[float]] = get_bounds(flat_list)

    def __get_valids(self, points: list[list[tuple[float, float] | str]]) -> int:
        """
        returns the number of valid points in the points passed to the CellMap

        Parameters
        ----------
        points : list[list[tuple[float, float] | str]]
            the points that define the CellMap's data

        Returns
        -------
        num_valids : int
            the number of valid cells in the cell map
        """

        count: int = 0
        i: int
        j: int
        for i in range(len(points)):
            for j in range(len(points[0])):
                if points[i][j] != "X":
                    count += 1
        return count

    def __init_map(
        self, points: list[list[tuple[float, float] | str]], odlc_count: int
    ) -> list[list[Cell]]:
        """
        This method creates the two-dimensional array filled with Cell
        objects used by the CellMap.

        Parameters
        ----------
        points : list[list[tuple[float, float] | str]]
            A two-dimensional array of latitude and longitude points that defines
            the search area
        odlc_count : int
            the number of ODLCs in the search area

        Returns
        -------
        final_map : list[list[Cell]]
            the two-dimensional list of cell objects
        """
        final_map: list[list[Cell]] = []
        i: int
        j: int
        for i in range(len(points)): #pylint: disable=C0200
            row: list[Cell] = []
            for j in range(len(points[0])):
                if points[i][j] != "X":  # ensures it is not the only used string value
                    row.append(
                        Cell(
                            odlc_count / self.num_valids,
                            False,
                            points[i][j][0],  # type: ignore
                            points[i][j][1],  # type: ignore
                            True,
                        )
                    )
                else:
                    row.append(Cell(0, False, -1.0, -1.0, False))
            final_map.append(row)
        return final_map

    def __getitem__(self, index: int) -> list[Cell]:
        return self.data[index]

    def display(self) -> None:
        """
        Prints out the current CellMap in the standard output.
        """
        i: int
        j: int
        for i in range(len(self.data)):
            row_string: str = ""
            for j in range(len(self.data[0])):
                if not self.data[i][j].is_valid:
                    row_string += " "
                else:
                    row_string += "X"
            print(row_string)

