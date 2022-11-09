from copy import deepcopy
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

def get_seen_map(cell_map : CellMap) -> List[List[bool]]:
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
            row.append(cell_map[i][j].seen)
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

    print(seen_search(seeker, cell_map, 3))
