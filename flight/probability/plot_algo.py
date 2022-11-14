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
    def get_num_valids(self):
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
        self.move_list = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.shortest_path = float("inf")

    def get_valid_positions(self,history: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Given some position on the compressed map, return all possible moves

        Parameters
        ----------
        pos : Tuple[int, int]
            The current i, j position

        Returns
        -------
        moves : List[Tuple[int, int]]
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

    def valid_solution(self, solution: List[Tuple[int, int]]) -> bool:
        """
        Checks if the candidate list contains all valid coordinates of the compressed map

        Parameters
        ----------
        solution : List[Tuple[int, int]]
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

    def find_unseens(self, history : List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        history_set = set(history) # O(1) lookup time
        return_list = []
        for i in range(len(self.compressed)):
            for j in range(len(self.compressed[0])):
                if (i, j) not in history_set:
                    return_list.append((i, j))
        return return_list

    def in_corner(self, pos: Tuple[int, int], history: list[Tuple[int, int]]) -> List[Tuple[int, int]]:
        shortest_len, shortest_path = float("inf"), [0, 0]

        start = self.a_star_grid.node(pos[1], pos[0])
        for unseen in list(filter(lambda x: self.compressed[x[0]][x[1]] != 0, self.find_unseens(history))):
            self.a_star_grid.cleanup()
            end = self.a_star_grid.node(unseen[1], unseen[0])
            path, _ = self.a_star.find_path(start, end, self.a_star_grid)
            if len(path) < shortest_len:
                shortest_len = len(path)
                shortest_path = path

        return [(x[1], x[0]) for x in shortest_path[1:]]

    def breadth_search(self, start: Tuple[int, int]) -> List[Tuple[int, int]]:
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
                histories.append(new_history)
            
if __name__ == "__main__":
    area = segment(TEST_AREA)
    cell_map = CellMap(area, 30)
    seeker = Seeker((4, 108), 1, 4, cell_map)
    c = Compressor.compress(8, cell_map)
    s = Searcher(cell_map, 8)

    #print(s.breadth_search((1, 4)))

    import cProfile
    cProfile.run('s.breadth_search((1, 4))')
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
