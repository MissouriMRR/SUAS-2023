from typing import Any, List, Tuple
from cell import Cell
from helper import get_bounds
from segmenter import segment

class CellMap:
    """
    a two-dimensional array where the row element's are square segments of the
    search area, each associated with some probability of having an ODLC

    Attributes
    ----------
    points : List[List[Tuple[float, float] | str]]
        a two-dimensional array of latitude and longitude points that defines
        the search area
    ODLCs : int
        the number of ODLCs on the map. Used to calculate the initial 
        probabilities of each cell.
    """
    
    def __get_valids(self, points: List[List[Tuple[float, float] | str]]) -> int:
        """
        returns the number of valid points in the points passed to the CellMap

        Parameters
        ----------
        points : List[List[Tuple[float, float] | str]]
            the points that define the CellMap's data

        Returns
        -------
        num_valids : int
            the number of valid cells in the cell map
        """

        count = 0
        for i in range(len(points)):
            for j in range(len(points[0])):
                if points[i][j] != 'X': count += 1
        return count

    def __init_map(self, points: List[List[Tuple[float, float] | str]], ODLCs: int) -> List[List[Cell]]:
        """
        This method creates the two-dimensional array filled with Cell 
        objects used by the CellMap.

        Parameters
        ----------
        points : List[List[Tuple[float, float] | str]]
            A two-dimensional array of latitude and longitude points that defines
            the search area
        ODLCs : int
            the number of ODLCs in the search area

        Returns
        -------
        final_map : List[List[Cell]]
            the map of cell objects
        """
        r_list: List[List[Cell]] = []
        for i in range(len(points)):
            row: List[Cell] = []
            for j in range(len(points[0])):
                if points[i][j] != 'X': #ensures it is not the only used string value
                    row.append(Cell(ODLCs / self.n, False, points[i][j][0], points[i][j][1], True)) #type: ignore
                else:
                    row.append(Cell(0, False, None, None, False))
            r_list.append(row)
        return r_list

    def __getitem__(self, index: int) -> List[Cell]:
        return self.data[index]

    def display(self, drone_pos: Tuple[int, int] | None = None) -> None:
        """
        Prints out the current CellMap in the standard output.

        Parameters
        ----------
        drone_pos : Tuple[int, int] | None
            optional parameter for the drone's current index
        """
        for i in range(len(self.data)):
            row_string = ""
            for j in range(len(self.data[0])):
                if not self.data[i][j].is_valid:
                    row_string += ' '
                elif drone_pos == (i, j):
                    row_string += 'S'
                else:
                    row_string += 'X'
            print(row_string)

    #TODO: FINISH THIS METHOD!
    #TODO: Fix the seeker type. Seeker module imports cell_map module, so
          #create new type with typing?
    def update_probs(self, pos: Tuple[int, int], seeker: Any) -> None:
        """
        Given a drone at position pos[0], pos[1], this function updates the probabalities
        of each cell to reflect that the seeker has observed them.

        Parameters
        ----------
        pos : Tuple[int, int]
            the index of the drone
        seeker : Seeker
            the seeker object, including its find_prob and other attributes
        """

        for disp_vec in seeker.view_vecs:
            try:
                poi = (pos[0] + disp_vec[0], pos[1] + disp_vec[1])
                if poi[0] >= 0 and poi[1] >= 0 and poi not in seeker.current_view:
                    self[poi[0]][poi[1]].probability *= 1 - seeker.find_prob
                    self[poi[0]][poi[1]].seen = True
                    
            except:
                pass

    def __init__(self, points: List[List[Tuple[float, float] | str]], ODLCs: int = 1) -> None:
        """
        Parameters
        ----------
        points : List[List[Tuple[float, float] | str]]
            a collection of latitude, longitude coordinates to define the map
        ODLCs : int
            the number of ODLCs in the flight area
        """
        self.n = self.__get_valids(points)
        self.data = self.__init_map(points, ODLCs)

        flat_list = []
        for sub_list in self.data:
            for item in sub_list:
                if item.x is not None and item.y is not None:
                    flat_list.append((item.x, item.y))
        self.bounds = get_bounds(flat_list)


if __name__ == "__main__":
    test_cloud = [
        (38.31722979755967,-76.5570186342245),
        (38.3160801028265,-76.55731984244503),
        (38.31600059675041,-76.5568902018946),
        (38.31546739500083,-76.5537620127769),
        (38.31470980862425,-76.5493636141453),
        (38.31424154692598,-76.5466276164690),
        (38.31369801280048,-76.5434238005822),
        (38.3131406794544,-76.54011767488228),
        (38.31508631356025,-76.5396286507867),
        (38.31615083692682,-76.5449773879351),
        (38.31734210679102,-76.5446085046679),
        (38.31859044679581,-76.5519329158383),
        (38.3164700703248,-76.55255360208943),
        (38.31722979755967,-76.5570186342245)
    ]
    area = segment(test_cloud)
    cell_map = CellMap(area, 4)
