"""
Summary
-------
Defines the seeker class and contains basic tests
"""

from typing import Tuple, List
from cell_map import CellMap
from helper import calculate_dist
from cell import Cell


# TODO: replace view radius attribute with height and view angle
class Seeker:
    """
    The simulated drone used in the search algorithm

    Attributes
    ----------
    start : Tuple[int]
        the starting index of the drone
    find_prob : float
        the probability of the drone finding an ODLC in a cell within its view
    view : int
        the radius of the cell view
    cell_map : CellMap
        the actual map being searched
    current_view : List[Cell]
        a list of all points within range of the drone
    """

    def __get_view_vecs(self, view: int) -> List[Tuple[int, int]]:
        """
        returns a list of displacement vectors that can be seen from the drone
        based upon its range.

        Parameters
        ----------
        view : int
            The range of the drone view

        Returns
        -------
        view_vectors : List[Tuple[int]]
            The displacement vectors in view of the drone
        """

        view_list = []

        for i in range(view * 2 + 1):
            for j in range(view * 2 + 1):
                if calculate_dist((i, j), (view, view)) <= view:
                    view_list.append((i - view, j - view))
        return view_list

    def __init__(
        self, start: Tuple[int, int], find_prob: float, view: int, cell_map: CellMap
    ) -> None:
        """
        Attributes
        ----------
        start : Tuple[int]
            the starting index of the drone
        find_prob : float
            the probability of the drone finding an ODLC in a cell within its view
        view : int
            the radius of the cell view
        cell_map : CellMap
            The actual map being searched
        """
        self.pos = start
        self.find_prob = find_prob  # probability of finding object when cell is in view
        self.view = view
        self.view_vecs = self.__get_view_vecs(view)
        self.current_view: List[Cell] = []  # a set of points that the drone is currently looking at
        self.cell_map = cell_map

    def get_in_view(self) -> List[Cell]:
        """
        gets the points currently being looked at by the drone

        Returns
        -------
        cells_in_view : List[Cell]
        """
        in_view = []
        for disp_vec in self.view_vecs:
            try:
                poi = (self.pos[0] + disp_vec[0], self.pos[1] + disp_vec[1])
                if poi[0] >= 0 and poi[1] >= 0 and self.cell_map[poi[0]][poi[1]].is_valid:
                    in_view.append(self.cell_map[poi[0]][poi[1]])
            except:
                pass

        return in_view

    def move(self, disp_vec: Tuple[int, int]) -> None:
        """
        moves the drone on the cell_map

        disp_vec : Tuple[int, int]
            The direction the drone should move
            ex : [1, 0] moves the drone up.
        """
        try:
            new_pos = (self.pos[0] + disp_vec[0], self.pos[1] + disp_vec[1])

            if self.cell_map[new_pos[0]][new_pos[1]].is_valid:
                self.cell_map.update_probs(new_pos, self)
                self.pos = new_pos
                self.current_view = self.get_in_view()
            else:
                pass
        except:
            pass


if __name__ == "__main__":
    s = Seeker((0, 0), 0.9, 5, CellMap([[(0, 0)]]))
    space = s.get_in_view()
    for cell in space:
        print(cell)
