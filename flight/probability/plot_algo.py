"""
The actual algorithm powering the drone's navigation
"""

from math import floor, sqrt
from bisect import insort
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.grid import Grid
from numpy import zeros, int8
from cell_map import CellMap
from helper import AIR_DROP_AREA
from segmenter import segment, rotate_shape, SUAS_2023_THETA

class Compressor:
    """
    Compresses the search area into a low resolution graph based on the drone's
    search area, exponentially reducing the time the algorithm takes

    Methods
    -------
    analyze_cell(i : int, j: int, s: int, cell_map: CellMap) -> int
        Returns the number of in-bounds cells
    get_circum_square_r(r: int) -> int
        returns the side length of the square inside the view radius circle
    __init_compressed_grid(cell_size : int, cell_map : CellMap) -> list[list[int]]:
        Returns empty compressed grid with correct dimensions
    compress(radius: int, cell_map: CellMap) -> list[list[tuple[bool, int, int]]]
        compresses the given cell_map into larger cells based on the given radius
    
    """

    @staticmethod
    def analyze_cell(i: int, j: int, s: int, cell_map: CellMap) -> int:
        """
        Given the compressed index, returns the number of valid locations
        within the cell

        Parameters
        ----------
        i : int
            the row of the compressed cell
        j : int
            the column of the compressed cell
        cell_map : CellMap
            the map being compressed

        Returns
        -------
        value : int
            the number of valid cells within the compressed cell
        """
        score: int = 0
        row_start: int = s * i
        row_end: int = min((s * (i + 1) - 1), len(cell_map.data) - 1)
        col_start: int = s * j
        col_end: int = min((s * (j + 1) - 1), len(cell_map[0]) - 1)

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

        return r# max(floor(sqrt(r/2)), 1)

    @staticmethod
    def __init_compressed_grid(cell_size : int, cell_map : CellMap) -> list[list[int]]:
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
        empty_grid : list[list[int]]
            an empty grid of three points repres
        """
        cols: int = floor(len(cell_map[0]) / cell_size)
        rows: int = floor(len(cell_map.data) / cell_size)
        return zeros((rows, cols), dtype=int8)

    @staticmethod
    def compress(radius: int, cell_map: CellMap) -> list[list[tuple[bool, int, int]]]:
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
        compressed_map : list[list[tuple[bool, int, int]]]
            A compressed map with cells of the form
            bool -> seen
            int -> value
            int -> dist
        """
        s: int = Compressor.get_circum_square_r(radius)
        new_grid: list[list[int]] = Compressor.__init_compressed_grid(s, cell_map)
        for i in range(len(new_grid)):
            for j in range(len(new_grid[0])):
                new_grid[i][j] = Compressor.analyze_cell(i, j, s, cell_map)
        return new_grid

class Searcher:
    """
    Performs a breath-first search looking for paths that stop by all cells
    """
    def get_num_valids(self):
        """
        Retuns the number of valid compressed cells
        """
        num = 0
        for i in range(len(self.compressed)):
            for j in range(len(self.compressed[0])):
                if self.compressed[i][j] != 0:
                    num += 1
        return num

    def __init__(self, cell_map : CellMap, view_radius : int):
        self.compressed = Compressor.compress(view_radius, cell_map)
        self.n = self.get_num_valids()
        self.view_radius = view_radius
        self.a_star = AStarFinder()
        self.a_star_grid = Grid(matrix=self.compressed)
        self.move_list = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]
        self.shortest_path = float("inf")

    def get_valid_positions(self, history: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        Given a list of moves already made on the compressed map,
        return all possible immediate moves.

        Parameters
        ----------
        history : list[tuple[int, int]]
            list of i, j positions visited thus far

        Returns
        -------
        moves : list[tuple[int, int]]
            A list of possible moves
        """
        pos = history[-1]
        hist_set = set(history)
        moves = []
        for move in self.move_list:
            if (
                    0 <= pos[0] + move[0] < len(self.compressed) and
                    0 <= pos[1] + move[1] < len(self.compressed[0]) and
                    self.compressed[pos[0] + move[0]][pos[1] + move[1]] != 0 and
                    (pos[0] + move[0], pos[1] + move[1]) not in hist_set
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

        cand_set = set(solution) #O(1) lookup times

        for i in range(len(self.compressed)):
            for j in range(len(self.compressed[0])):
                if self.compressed[i][j] != 0 and (i, j) not in cand_set:
                    return False
        return True

    def find_unseens(self, history : list[tuple[int, int]]) -> list[tuple[int, int]]:
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
        history_set = set(history) # O(1) lookup time
        return_list = []
        for i in range(len(self.compressed)):
            for j in range(len(self.compressed[0])):
                if (i, j) not in history_set:
                    return_list.append((i, j))
        return return_list
 
    def find_closest(self, points: list[tuple[int, int]], px: tuple[int, int]) -> tuple[int, int]:
        """
        Finds the closest point in terms of Euclidean distance

        Parameters
        ----------
        points : list[tuple[int, int]]
            the points to be pruned
        px : tuple[int, int]
            the point the distances are relative to

        Returns
        -------
        closest_point : tuple[int, int]
            The coordinates of the closest point
        """
        closest = None
        closest_dist = float("inf")
        for point in points:
            dist = abs(point[0] - px[0]) + abs(point[1] - px[1])
            if dist < closest_dist:
                closest_dist = dist
                closest = point
        return closest

    def in_corner(self, pos: tuple[int,int], history: list[tuple[int,int]])->list[tuple[int, int]]:
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

        approx_nearest = self.find_closest(self.find_unseens(history), pos)
        start = self.a_star_grid.node(pos[1], pos[0])
        end = self.a_star_grid.node(approx_nearest[1], approx_nearest[0])
        self.a_star_grid.cleanup()
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
        histories = [[start]]
        while len(histories) != 0:
            history = histories.pop(0)
            if len(history) >= self.n:
                if self.valid_solution(history):
                    return history

            possible_moves = self.get_valid_positions(history)
            if len(possible_moves) == 0:
                history += self.in_corner(history[-1], history)
                possible_moves = self.get_valid_positions(history)

            for move in possible_moves:
                new_history = list(history)
                new_history.append(move)
                insort(histories, new_history, key=lambda x: len(x))

class Decompressor:

    @staticmethod
    def __prep_grid(cell_map: CellMap):
        new_grid = zeros((len(cell_map.data), len(cell_map[0])))
        for i in range(len(cell_map.data)):
            for j in range(len(cell_map[0])):
                if cell_map[i][j].is_valid:
                    new_grid[i][j] = 1
        return new_grid

    @staticmethod
    def get_valid_point(point, cell_map, cell_size):
        cell_map.display()
        point = (point[0] * cell_size, point[1] * cell_size)
        middle = cell_size // 2
        closest = float("inf")
        closest_point = (point[0] + middle, point[1] + middle)
        for i in range(cell_size):
            for j in range(cell_size):
                try:
                    if cell_map[point[0] + i][point[1] + j].is_valid:
                        dist = sqrt((middle - i)**2 + (middle - j)**2)
                        if dist < closest:
                            closest = dist
                            closest_point = (point[0] + i, point[1] + j)
                except:
                    pass
        return closest_point

    @staticmethod
    def __decompress_point(point: tuple[int, int], cell_map: CellMap, cell_size: int):
        new_x = point[1] * cell_size + (cell_size // 2)
        new_y = point[0] * cell_size + (cell_size // 2)

        if cell_map[new_y][new_x].is_valid:
            return (new_y, new_x)
        else:
            return Decompressor.get_valid_point(point, cell_map, cell_size)

    @staticmethod
    def decompress_route(route: list[tuple[int, int]], cell_map: CellMap, cell_size: int):
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
        prepped_grid = Decompressor.__prep_grid(cell_map)
        search_grid = Grid(matrix=prepped_grid)
        finder = AStarFinder()
        for i in range(len(route)):
            route[i] = Decompressor.__decompress_point(route[i], cell_map, cell_size)
        new_path = []
        for i in range(len(route) - 1):
            search_grid.cleanup()
            A = search_grid.node(route[i][1], route[i][0])
            B = search_grid.node(route[i+1][1], route[i+1][0])
            A_to_B, _ = finder.find_path(A, B, search_grid)
            
            if i == len(route) - 2:
                new_path += A_to_B[:-1]
            else:
                new_path += A_to_B

        return new_path

def get_plot():
    """
    Gets the coordinates list for SUAS 2023
    """
    area = segment(rotate_shape(AIR_DROP_AREA, SUAS_2023_THETA, AIR_DROP_AREA[0]), 0.000025)

    cell_map = CellMap(area, 5)
    cell_map.display()
    s = Searcher(cell_map, 8)

    path = Decompressor.decompress_route(s.breadth_search((0, 0)), cell_map, 8)
    coordinate_list = []
    for point in path:
        cell_map_point = cell_map[point[1]][point[0]]
        coordinate_list.append((cell_map_point.lat, cell_map_point.lon))
    return coordinate_list



if __name__ == "__main__":
    print(get_plot())

    #import cProfile
    #cProfile.run('s.breadth_search((1, 4))')
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
