"""
The actual algorithm powering the drone's navigation
"""

# pylint: disable=C0200
#NOTE: removes "consider using enumerate" error

from math import floor, sqrt
from bisect import insort
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid, Node
import numpy as np
from nptyping import Int8, NDArray, Shape
from flight.search.cell_map import CellMap
from flight.search.cell import Cell
from flight.search.helper import AIR_DROP_AREA
from flight.search.segmenter import segment, rotate_shape, SUAS_2023_THETA


class Compressor:
    """
    Compresses the search area into a low resolution graph based on the drone's
    search area, exponentially reducing the time the algorithm takes

    Methods
    -------
    analyze_cell(i : int, j: int, s: int, cell_map: CellMap) -> int
        Returns the number of in-bounds cells
        returns the side length of the square inside the view radius circle
    __init_compressed_grid(cell_size : int, cell_map : CellMap) ->  NDArray[Shape["*, *"], Int8]:
        Returns empty compressed grid with correct dimensions
    compress(radius: int, cell_map: CellMap) -> NDArray[Shape["*, *"], Int8]
        compresses the given cell_map into larger cells based on the given radius
    """

    @staticmethod
    def analyze_cell(row: int, col: int, size: int, cell_map: CellMap) -> int:
        """
        Given the compressed index, returns the number of valid locations
        within the cell

        Parameters
        ----------
        row : int
            the row of the compressed cell
        col : int
            the column of the compressed cell
        size: int
            size of the cell
        cell_map : CellMap
            the map being compressed

        Returns
        -------
        value : int
            the number of valid cells within the compressed cell
        """
        score: int = 0
        row_start: int = size * row
        row_end: int = min((size * (row + 1) - 1), len(cell_map.data) - 1)
        col_start: int = size * col
        col_end: int = min((size * (col + 1) - 1), len(cell_map[0]) - 1)

        for i in range(row_start, row_end + 1):
            for j in range(col_start, col_end + 1):
                try:
                    if cell_map[i][j].is_valid:
                        score += 1
                except IndexError:
                    pass

        return score

    @staticmethod
    def __init_compressed_grid(cell_size: int, cell_map: CellMap) -> NDArray[Shape["*, *"], Int8]:
        """
        Returns an empty grid for the compressed map

        Parameters
        ----------
        cell_size : int
            the side length of each square cell
        cell_map : CellMap
            the map being compressed

        Returns
        -------
        empty_grid : NDArray[Shape['*, *'], Int8]
            an empty grid of three points repres
        """
        cols: int = floor(len(cell_map[0]) / cell_size)
        rows: int = floor(len(cell_map.data) / cell_size)
        return np.zeros((rows, cols), dtype=np.int8)

    @staticmethod
    def compress(radius: int, cell_map: CellMap) -> NDArray[Shape["*, *"], Int8]:
        """
        Given a view radius, r, compress the binary map of the search area
        into cells with size r' and weight equal to their valid cell area.

        Parameters
        ----------
        radius : int
            The view radius of the drone
        seen_area : list[list[bool]]
            The uncompressed map

        Returns
        -------
        compressed_map : NDArray[Shape['*, *'], Int8]
            A compressed map with three-dimensional cells representing
            whether a cell has been seen (bool), what how many subcells
            are within it (int) and its distance (int)
        """
        new_grid: NDArray[Shape["*, *"], Int8] = Compressor.__init_compressed_grid(radius, cell_map)
        i: int
        j: int
        for i in range(len(new_grid)):
            for j in range(len(new_grid[0])):
                new_grid[i][j] = Compressor.analyze_cell(i, j, radius, cell_map)
        return new_grid


class Searcher:
    """
    Performs a breath-first search looking for paths that stop by all cells

    Attributes
    ----------
        compressed: NDArray[Shape['*, *'], Int8]
            the compressed array that is being searched
        num_valids: int
            number of valid cells in array (excludes empty cells, for example)
        a_star: AStarFinder
            the A* searcher object, used as class variable to avoid overhead of
            repeated initializations
        a_star_grid: Grid
            the A* search grid, used as class variable to avoid overhead of
            repeated initializations
        move_list: list[tuple[int, int]]
            the list of valid moves in the grid ((1, 1) represents moving diagonally,
            for example)

    Methods
    -------
    get_num_valids() -> int
        returns number of non-empty cells
    get_valid_moves(history: list[tuple[int, int]]) -> list[tuple[int, int]]
        returns all possible moves based on the current position
    valid_solution(solution: list[tuple[int, int]]) -> bool
        determines if a given path touches all cells
    find_unseens(history: list[tuple[int, int]]) -> list[tuple[int, int]]
        finds all cells not visited in the given path
    find_closest(points: list[tuple[int, int]], px: tuple[int, int]) -> tuple[int, int]
        finds the closest point to px
    in_corner(pos: tuple[int, int], history[list[tuple[int, int]]])
        returns the path to escape the given corner
    breadth_search(start: tuple[int, int]) -> list[tuple[int, int]]
        returns the shrotest circuit route through all cells.
    """

    def __init__(self, cell_map: CellMap, view_radius: int) -> None:
        """
        Initializes the object

        Parameters
        ----------
        cell_map: CellMap
            the cell map being searched
        view_radius: int
            how many cells away the searcher can see
        """
        self.compressed: NDArray[Shape["*, *"], Int8] = Compressor.compress(view_radius, cell_map)
        self.num_valids: int = self.get_num_valids()
        self.a_star: AStarFinder = AStarFinder()
        self.a_star_grid: Grid = Grid(matrix=self.compressed)
        self.move_list: list[tuple[int, int]] = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, -1),
        ]

    def get_num_valids(self) -> int:
        """
        Returns the number of valid compressed cells

        Returns
        -------
        num_valids: int
            The number of valid compressed cells
        """
        num: int = 0
        i: int
        j: int
        for i in range(len(self.compressed)):
            for j in range(len(self.compressed[0])):
                if self.compressed[i][j] != 0:
                    num += 1
        return num

    def get_valid_moves(self, history: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        Given a list of moves already made on the compressed map,
        return all possible immediate moves.

        Parameters
        ----------
        history : list[tuple[int, int]]
            list of row, column positions visited thus far

        Returns
        -------
        moves : list[tuple[int, int]]
            A list of possible moves
        """
        pos: tuple[int, int] = history[-1]
        hist_set: set[tuple[int, int]] = set(history)
        moves: list[tuple[int, int]] = []
        move: tuple[int, int]

        for move in self.move_list:
            if (
                0 <= pos[0] + move[0] < len(self.compressed)
                and 0 <= pos[1] + move[1] < len(self.compressed[0])
                and self.compressed[pos[0] + move[0]][pos[1] + move[1]] != 0
                and (pos[0] + move[0], pos[1] + move[1]) not in hist_set
            ):
                moves.append((pos[0] + move[0], pos[1] + move[1]))
        return moves

    def valid_solution(self, solution: list[tuple[int, int]]) -> bool:
        """
        Checks if the candidate list contains all valid coordinates of the compressed map

        Parameters
        ----------
        solution : list[tuple[int, int]]
            The path being examined

        Returns
        -------
        contains_all : bool
            Whether all coordinates are in the candidates list
        """

        cand_set: set[tuple[int, int]] = set(solution)  # O(1) lookup times

        i: int
        j: int
        for i in range(len(self.compressed)):
            for j in range(len(self.compressed[0])):
                if self.compressed[i][j] != 0 and (i, j) not in cand_set:
                    return False
        return True

    def find_unseens(self, history: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        finds all unvisited compressed cells

        Parameters
        ----------
        history : list[tuple[int, int]]
            the list of all cells visited thus far

        Returns
        -------
        unseen_points : list[tuple[int, int]]
            list of all unseen cells
        """
        history_set: set[tuple[int, int]] = set(history)  # O(1) lookup time
        return_list: list[tuple[int, int]] = []
        i: int
        j: int
        for i in range(len(self.compressed)):
            for j in range(len(self.compressed[0])):
                if (i, j) not in history_set:
                    return_list.append((i, j))
        return return_list

    def find_closest(
        self, points: list[tuple[int, int]], cur_point: tuple[int, int]
    ) -> tuple[int, int]:
        """
        Finds the closest point in terms of Euclidean distance

        Parameters
        ----------
        points : list[tuple[int, int]]
            the points to be pruned
        cur_point : tuple[int, int]
            the point the distances are relative to

        Returns
        -------
        closest_point : tuple[int, int]
            The coordinates of the closest point
        """
        closest: tuple[int, int] = (-1, -1)
        closest_dist: float = float("inf")
        point: tuple[int, int]
        for point in points:
            dist: int = abs(point[0] - cur_point[0]) + abs(point[1] - cur_point[1])
            if dist < closest_dist:
                closest_dist = dist
                closest = point
        return closest

    def in_corner(
        self, pos: tuple[int, int], history: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """
        function to get the searcher out of a corner to the closest
        undiscovered cell

        Parameters
        ----------
        pos : tuple[int, int]
            the current position
        history : list[tuple[int, int]]
            list of all visited points

        Returns
        -------
        escape_path : list[tuple[int, int]]
            the path to reach the nearest unexplored cell
        """

        approx_nearest: tuple[int, int] = self.find_closest(self.find_unseens(history), pos)
        start: Node = self.a_star_grid.node(pos[1], pos[0])
        end: Node = self.a_star_grid.node(approx_nearest[1], approx_nearest[0])
        self.a_star_grid.cleanup()
        path: list[tuple[int, int]]
        path, _ = self.a_star.find_path(start, end, self.a_star_grid)

        return [(x[1], x[0]) for x in path[1:]]

    def breadth_search(self, start: tuple[int, int]) -> list[tuple[int, int]]:
        """
        A breadth based search algorithm to find the shortest path
        to visit all cells

        Parameters
        ----------
        start: tuple[int, int]
            the starting position, in terms of the compressed cell

        Returns
        -------
        shortest_path : list[tuple[int, int]]
            A list of points that defines the shortest continous path
            that visits all points in the compressed grid.
        """
        histories: list[list[tuple[int, int]]] = [[start]]
        while len(histories) != 0:
            history: list[tuple[int, int]] = histories.pop(0)
            if len(history) >= self.num_valids:
                if self.valid_solution(history):
                    return history

            possible_moves: list[tuple[int, int]] = self.get_valid_moves(history)
            if len(possible_moves) == 0:
                history += self.in_corner(history[-1], history)
                possible_moves = self.get_valid_moves(history)

            move: tuple[int, int]
            for move in possible_moves:
                new_history = list(history)
                new_history.append(move)
                insort(histories, new_history, key=len)
        return [(-1, -1)]  # mypy was not happy with only the conditional return statement


class Decompressor:
    """
    Takes the path calculated for a compressed grid and uncompresses it
    to return the actual coordinates.

    Methods
    -------
    __prep_grid(cell_map: CellMap) -> NDArray[Shape["*, *"], Int8]
        turns the CellMap into a numpy array
    get_valid_point(point: tuple[int, int], cell_map: CellMap, cell_size: int) -> tuple[int, int]
        given coordinates outside the bounded area, find the nearest point inside the area
    __decompress_point(point: tuple[int, int], cell_map: CellMap, cell_size: int) -> tuple[int, int]
        given the coordinates of a compressed point, return the uncompressed coordinates in the
        center of that point
    decompress_route(
        route: list[tuple[int, int]],
        cell_map: CellMap, cell_size: int
        ) -> list[tuple[int, int]]

        given a compressed path, return the uncompressed path
    """

    @staticmethod
    def __prep_grid(cell_map: CellMap) -> NDArray[Shape["*, *"], Int8]:
        """
        Creates a numpy array of the given CellMap for faster computation

        Parameters
        ----------
        cell_map: CellMap
            the CellMap to turn into a numpy array

        Returns
        -------
        new_grid: NDArray[Shape["*, *"], Int8]
            the numpy version of the uncompressed CellMap
        """
        new_grid: NDArray[Shape["*, *"], Int8] = np.zeros(
            (len(cell_map.data), len(cell_map[0])), dtype=np.int8
        )
        i: int
        j: int

        for i in range(len(cell_map.data)):
            for j in range(len(cell_map[0])):
                if cell_map[i][j].is_valid:
                    new_grid[i][j] = 1
        return new_grid

    @staticmethod
    def get_valid_point(
        point: tuple[int, int], cell_map: CellMap, cell_size: int
    ) -> tuple[int, int]:
        """
        given coordinates outside the bounded area, find the nearest point inside the area

        Parameters
        ----------
        point: tuple[int, int]
            the point lying outside the bounded area
        cell_map: CellMap
            the CellMap being searched
        cell_size: int
            the size of the compressed cells

        Returns
        -------
        closest_point: tuple[int, int]
            the nearest point within the bounded area
        """
        cell_map.display()
        point = (point[0] * cell_size, point[1] * cell_size)
        middle: int = cell_size // 2
        closest: float = float("inf")
        closest_point: tuple[int, int] = (point[0] + middle, point[1] + middle)

        i: int
        j: int
        for i in range(cell_size):
            for j in range(cell_size):
                try:
                    if cell_map[point[0] + i][point[1] + j].is_valid:
                        dist: float = sqrt((middle - i) ** 2 + (middle - j) ** 2)
                        if dist < closest:
                            closest = dist
                            closest_point = (point[0] + i, point[1] + j)
                except IndexError:
                    pass
        return closest_point

    @staticmethod
    def __decompress_point(
        point: tuple[int, int], cell_map: CellMap, cell_size: int
    ) -> tuple[int, int]:
        """
        Given the coordinates of a compressed cell, return the uncompressed point directly
        in its middle

        Parameters
        ----------
        point: tuple[int, int]
            the compressed point coordinates
        cell_map: CellMap
            the map being searched
        cell_size: int
            the size of an compressed point relative to an uncompressed one

        Returns
        -------
        uncompressed_point: tuple[int, int]
            the coordinates of the uncompressed point
        """
        new_x: int = point[1] * cell_size + (cell_size // 2)
        new_y: int = point[0] * cell_size + (cell_size // 2)

        if cell_map[new_y][new_x].is_valid:
            return (new_y, new_x)
        return Decompressor.get_valid_point(point, cell_map, cell_size)

    @staticmethod
    def decompress_route(
        route: list[tuple[int, int]], cell_map: CellMap, cell_size: int
    ) -> list[tuple[int, int]]:
        """
        Takes the path generated using the compressed map and decompresses it
        to the original resolution of the CellMap.

        Parameters
        ----------
        route : list[tuple[int, int]]
            the compressed route
        cell_map : CellMap
            the original, uncompressed cell map
        cell_size : int
            the side length of the compressed cell

        Returns
        -------
        uncompressed_route : list[tuple[int, int]]
            the uncompressed route
        """
        prepped_grid: NDArray[Shape["*, *"], Int8] = Decompressor.__prep_grid(cell_map)
        search_grid: Grid = Grid(matrix=prepped_grid)
        finder: AStarFinder = AStarFinder()

        i: int
        for i in range(len(route)):
            route[i] = Decompressor.__decompress_point(route[i], cell_map, cell_size)
        new_path: list[tuple[int, int]] = []

        for i in range(len(route) - 1):
            search_grid.cleanup()
            start: Node = search_grid.node(route[i][1], route[i][0])
            end: Node = search_grid.node(route[i + 1][1], route[i + 1][0])
            path: list[tuple[int, int]]
            path, _ = finder.find_path(start, end, search_grid)

            if i == len(route) - 2:
                new_path += path[:-1]
            else:
                new_path += path

        return new_path


def get_plot() -> list[tuple[float, float]]:
    """
    Gets the coordinates list for SUAS 2023

    Returns
    -------
    list[tuple[float, float]]
    """
    area: list[list[tuple[float, float] | str]] = segment(
        rotate_shape(AIR_DROP_AREA, SUAS_2023_THETA, AIR_DROP_AREA[0]),
        0.000025,
        SUAS_2023_THETA,
        AIR_DROP_AREA[0],
    )

    cell_map: CellMap = CellMap(area, 5)
    cell_map.display()
    searcher: Searcher = Searcher(cell_map, 8)

    path: list[tuple[int, int]] = Decompressor.decompress_route(
        searcher.breadth_search((0, 0)), cell_map, 8
    )
    coordinate_list: list[tuple[float, float]] = []
    point: tuple[int, int]
    for point in path:
        cell_map_point: Cell = cell_map[point[1]][point[0]]
        coordinate_list.append((cell_map_point.lat, cell_map_point.lon))
    return coordinate_list


if __name__ == "__main__":
    pass
