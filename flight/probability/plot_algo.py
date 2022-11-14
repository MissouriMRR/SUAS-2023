from math import floor, sqrt
from copy import deepcopy
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid
from numpy import zeros, ndarray, int8, ones
from seeker import Seeker
from cell_map import CellMap
from typing import List, Tuple
from helper import TEST_AREA
from segmenter import segment

class Compressor:

    @staticmethod
    def analyze_cell(i: int, j: int, s: int, cell_map: CellMap) -> int:
        """
        Given the compressed index, returns the value of the cell
        """
        score = 0
        row_start = s * i
        row_end = min((s * (i + 1) - 1), len(cell_map.data) - 1)
        col_start = s * j
        col_end = min((s * (j + 1) - 1), len(cell_map[0]) - 1)

        for row in range(row_start, row_end + 1):
            for col in range(col_start, col_end + 1):
                try:
                    if cell_map[row][col].is_valid:
                        score += 1
                except: pass

        return score

    @staticmethod
    def get_circum_square_r(r: int) -> int:
        """
        Given the view radius of the seeker, return the radius of the 
        circumscribed square that lies within it

        Parameters
        ----------
        r : int
            Radius of the circle

        Returns
        -------
        s : int
            side length of the square
        """

        return max(floor(sqrt(2) * r), 1)

    @staticmethod
    def __init_compressed_grid(cell_size : int, cell_map : CellMap) -> List[List[Tuple[bool, int, int]]]:
        """
        Returns an empty grid for the compressed map
        """
        cols = floor(len(cell_map[0]) / cell_size)
        rows = floor(len(cell_map.data) / cell_size)
        return zeros((rows, cols), dtype=int8)

    @staticmethod
    def compress(radius: int, cell_map: CellMap) -> List[List[Tuple[bool, int, int]]]:
        """
        Given a view radius, r, compress the binary map of the search area
        into cells with size r' and weight equal to their valid cell area.

        Parameters
        ----------
        radius : int
            The view radius of the drone
        seen_area : List[List[bool]]
            The uncompressed map
        
        Returns
        -------
        compressed_map : List[List[Tuple[bool, int, int]]]
            A compressed map with cells of the form
            bool -> seen
            int -> value
            int -> dist
        """
        s = Compressor.get_circum_square_r(radius)
        new_grid = Compressor.__init_compressed_grid(s, cell_map)
        for i in range(len(new_grid)):
            for j in range(len(new_grid[0])):
                new_grid[i][j] = Compressor.analyze_cell(i, j, s, cell_map)
        return new_grid

class Searcher:
    def __init__(self, cell_map : CellMap, view_radius : int):
        self.compressed = Compressor.compress(view_radius, cell_map)
        self.view_radius = view_radius
        self.a_star = AStarFinder()
        self.a_star_grid = Grid(matrix=self.compressed)

    


def get_valid_pos(area : ndarray, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Given some position on the compressed map, return all possible moves

    Parameters
    ----------
    area : ndarray
        The area being searched
    pos : Tuple[int, int]
        The current i, j position

    Returns
    -------
    moves : List[Tuple[int, int]]
        A list of possible moves
    """
    moves = []
    for move in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        if (
                0 <= pos[0] + move[0] < len(area) and
                0 <= pos[1] + move[1] < len(area[0]) and
                area[pos[0] + move[0]][pos[1] + move[1]] != 0
            ):
            moves.append((pos[0] + move[0], pos[1] + move[1]))
    return moves

def contains_all(compressed_map : ndarray, candidate: List[Tuple[int, int]]) -> bool:
    """
    Checks if the candidate list contains all valid coordinates of the compressed map

    Parameters
    ----------
    compressed_map : ndarray
        The area being checked
    candidate : List[Tuple[int, int]]
        The list of coordinates
    
    Returns
    -------
    contains_all : bool
        Whether all coordinates are in the candidates list
    """

    cand_set = set(candidate) #O(1) lookup times

    for i in range(len(compressed_map)):
        for j in range(len(compressed_map[0])):
            if compressed_map[i][j] != 0 and (i, j) not in cand_set:
                return False
    return True


def find_unseens(area : ndarray, history : List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    history_set = set(history) # O(1) lookup time
    return_list = []
    for i in range(len(area)):
        for j in range(len(area[0])):
            if (i, j) not in history_set:
                return_list.append((i, j))
    return return_list


def in_corner(area : ndarray, pos: Tuple[int, int], history: list[Tuple[int, int]]) -> List[Tuple[int, int]]:
    a_star_grid = Grid(matrix=area)
    finder = AStarFinder()
    shortest_len, shortest_path = float("inf"), [0, 0]

    start = a_star_grid.node(pos[1], pos[0])
    for unseen in list(filter(lambda x: area[x[0]][x[1]] != 0, find_unseens(area, history))):
        a_star_grid.cleanup()
        end = a_star_grid.node(unseen[1], unseen[0])
        path, _ = finder.find_path(start, end, a_star_grid)
        if len(path) < shortest_len:
            shortest_len = len(path)
            shortest_path = path

    return [(x[1], x[0]) for x in shortest_path[1:]]



def touch_all(compressed_map : ndarray, history : List[Tuple[int, int]], step=[float("inf")]) -> List[Tuple[int, int]]:
    """
    A recursive algorithm to find the shortest route through the compressed
    map, touching all cells as the drone goes through.

    Parameters
    ----------
    Compressed_map : ndarray
        The map being searched through
    history : List[Tuple[int, int]]
        All moves taken so far in this branch
    step : List[float]
        Due to function calls creating shallow copies of lists,
        allows the shortest path found so far to be shared across
        all function calls

    Returns
    -------
    shortest_path : List[Tuple[int, int]]
    """
    if contains_all(compressed_map, history):
        if len(history) < step[0]:
            step[0] = len(history)
            return history
        return None
    elif len(history) > step[0]:
        return None

    moves = []
    valid_positions = get_valid_pos(compressed_map, history[-1])
    candidate_moves = list(filter(lambda x : x not in history, valid_positions))
    if len(candidate_moves) == 0:
        history += in_corner(compressed_map, history[-1], history)
        valid_positions = get_valid_pos(compressed_map, history[-1])
        candidate_moves = list(filter(lambda x : x not in history, valid_positions))
    for move in candidate_moves:
        new_history = deepcopy(history)
        new_history.append(move)
        moves.append(touch_all(compressed_map, new_history, step))

    for move_set in moves:
        if move_set != None:
            if len(move_set) == step[0]:
                return move_set

    Exception("Something went wrong in 'touch_all'!")

if __name__ == "__main__":
    area = segment(TEST_AREA)
    cell_map = CellMap(area, 30)
    seeker = Seeker((4, 108), 1, 4, cell_map)
    c = Compressor.compress(8, cell_map)

    print(c)
    print(touch_all(c, [(2, 0)]))

    # TEST = [
    #     [1, 1, 1, 1, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 0, 0, 0],
    #     [1, 1, 1, 1, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 0, 1, 1, 1, 1],
    #     [0, 0, 0, 0, 1, 1, 1, 1],
    # ]
    # print(compress_area(4, TEST))
