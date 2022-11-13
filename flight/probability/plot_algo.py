from math import floor, sqrt
from copy import deepcopy
from numpy import zeros, ndarray, int8, ones
from seeker import Seeker
from cell_map import CellMap
from typing import List, Tuple
from helper import TEST_AREA
from segmenter import segment

# TODO: IMPLEMENT THE SEARACH ALGORITHM
def probability_catcher(seeker: Seeker, cell_map: CellMap, n: int = 10) -> None:
    """
    looks n moves into the future and tries to find a path with the largest
    probability per point.

    Parameters
    ----------
    seeker : Seeker
        the seeker object
    cell_map : CellMap
        the actual map being searched
    n : int
        the number of steps to look ahead
    """
    pass


def see_all_eval(seen_area : List[List[bool]]) -> int:
    """
    given a state represented by a grid of boolean values, returns the
    number of values that have been seen.

    Parameters
    ----------
    seen_area : List[List[bool]]
        the grid of the search area where seen cells are True and 
        unseen cells are False 
    """
    count = 0
    for row in seen_area:
        for cell in row:
            count += 1
    return count

def get_seen_map(cell_map : CellMap) -> List[List[int]]:
    """
    Given the cell map, returns a grid of boolean values representing
    whether the cell has been seen or not.

    Parameters
    ----------
    cell_map : CellMap
        The cell map object
    
    Returns
    -------
    seen_map : List[List[bool]]
        The binary map of seen cells.
    """
    final_map = []
    for i in range(len(cell_map.data)):
        row = []
        for j in range(len(cell_map[i])):
            if cell_map[i][j].is_valid:
                row.append(1 if cell_map[i][j].seen else -1)
            else:
                row.append(0)
        final_map.append(row)
    return final_map

def get_move_permutations(n: int = 10, moves: List[Tuple[int, int]] = [(1,0), (-1,0), (0,1), (0,-1)]) -> List[List[List[int]]]:
    """
    Returns all possible paths that can be taken

    Parameters
    ----------
    n : int
        The number of steps taken in each path
    
    Returns
    paths : List[List[List[int]]]
        A list of all possible permutations
    -------

    """
    perm1 = [[x] for x in moves]
    for _ in range(n - 1):
        perm2 = []
        for permutation in perm1:
            for vector in moves:
                p_mod = deepcopy(permutation)
                p_mod.append(vector)
                perm2.append(p_mod)
        perm1 = perm2
    
    return perm1

def sim(seeker : Seeker, cell_map : CellMap, path: List[List[Tuple[int, int]]]) -> CellMap:
    seeker = deepcopy(seeker)
    cell_map = deepcopy(cell_map)

    for move in path:
        seeker.move(move)
    return cell_map

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
    if contains_all(compressed_map, history) and len(history) < step[0]:
        step[0] = len(history)
        return history
    elif len(history) > step[0]:
        return None

    moves = []
    for move in list(filter(lambda x : x not in history, get_valid_pos(compressed_map, history[-1]))):
        new_history = deepcopy(history)
        new_history.append(move)
        moves.append(touch_all(compressed_map, new_history, step))

    for move_set in moves:
        if move_set != None:
            if len(move_set) == step[0]:
                return move_set

    Exception("Something went wrong in 'touch_all'!")

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

def init_compressed_grid(cell_size : int, uncompressed : List[List[bool]]) -> List[List[Tuple[bool, int, int]]]:
    """
    Returns an empty grid for the compressed map
    """
    cols = floor(len(uncompressed[0]) / cell_size)
    rows = floor(len(uncompressed) / cell_size)
    return zeros((rows, cols), dtype=int8)

def analyze_cell(i: int, j: int, s: int, uncompresed: List[List[bool]]) -> int:
    """
    Given the compressed index, returns the value of the cell
    """
    score = 0
    row_start = s * i
    row_end = min((s * (i + 1) - 1), len(uncompresed) - 1)
    col_start = s * j
    col_end = min((s * (j + 1) - 1), len(uncompresed[0]) - 1)

    for row in range(row_start, row_end + 1):
        for col in range(col_start, col_end + 1):
            try:
                if uncompresed[row][col] == -1:
                    score += 1
            except: pass

    return score

def compress_area(radius: int, seen_area : List[List[bool]]) -> List[List[Tuple[bool, int, int]]]:
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

    s = get_circum_square_r(radius)
    new_grid = init_compressed_grid(s, seen_area)
    for i in range(len(new_grid)):
        for j in range(len(new_grid[0])):
            new_grid[i][j] = analyze_cell(i, j, s, seen_area)
    return new_grid
    


def seen_search(seeker: Seeker, cell_map: CellMap, n: int = 5) -> None:
    permutations = get_move_permutations(n)
    counter = 1

    highest = float("-inf")
    best_perm = None
    for perm in permutations:
        counter += 1
        if counter % 100 == 0:
            print(f"{counter} / {len(permutations)}")
        outcome = see_all_eval(sim(seeker, cell_map, perm))
        if outcome > highest:
            highest = outcome
            best_perm = perm
    return best_perm


if __name__ == "__main__":
    area = segment(TEST_AREA)
    cell_map = CellMap(area, 30)
    seeker = Seeker((4, 108), 1, 4, cell_map)
    c = compress_area(8, get_seen_map(cell_map))

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
