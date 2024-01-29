"""
A knight is in a known cell on an empty chessboard and needs to reach another known cell.

Write a Python program that can take as input the two positions on the chessboard and returns as output:

* the set of all minimum-length sequences to move the piece from the initial cell to the final cell;
* a graphviz/dot file of the previous "all shortest path" graph.

Your code can use external libraries or you can avoid them as you wish. 
The case do not require machine learning specific algorithms or approaches.

Please provide also:

* a `requirements.txt`, if needed;
* a `Dockerfile` for the full environment, if you know how to create a `Dockerfile`;
* a short `README.md`.
"""

import argparse
import colorsys
import time
import os
import sys
from collections import deque
from abc import abstractmethod
from itertools import chain, product
from typing import List, Tuple, Set, Iterator, Dict
from graphviz import Digraph

MAX_WIDTH = 8
MAX_LENGTH = 8

def timeit(func):
    """
    Decorator Utility for measuring time

    :param func: function to measure
    :return: Tuple giving result and elapsed time
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    return wrapper

class Checkboard:
    """
    Class for structuring the checkboard and keeping the final solution file
    """

    def __init__(self, width, length):
        """
        :param width: Checkboard width
        :param length: Checkboard length
        """
        self.width = width
        self.length = length
        # graphviz file
        self.dot = None
    # Convenient static method to check if two points are equal
    @staticmethod
    def are_points_equal(point1 : Tuple[int, int], point2: Tuple[int, int]) -> bool:
        """
        Utility for checking if two points are equal. 
        Static because it's independent from the Checkboard
        :param point1: First point
        :param point2: Second point
        :return: Boolean that communicates if point1 is equal to point2
        """
        # Assertion for checking if points are really points
        assert len(point1) == len(point2) and len(point1) == 2
        return point1 == point2
    
    def create_chessboard_graphviz_file(self):
        """
        Utility function for creating a graphviz file
        """
        self.dot = Digraph(comment='Solution_Checkboard', engine='neato')
        
        # Define node style
        self.dot.attr('node', shape='square', style='filled', width='0.6', height='0.6')

        # Add nodes with alternating colors
        for row in range(self.width):
            for col in range(self.length):
                color = ('black', 'white') if (row + col) % 2 == 0 else ('white', 'black')
                self.dot.node(f'{row},{col}', fontcolor=color[1], fillcolor=color[0], pos=f'{col},{-row}!')

    def add_paths_to_graphviz(self, paths: Set):
        """
        Utility function for adding a path to graphviz
        :param paths: Set of shortest paths
        """
        if self.dot is None: 
            self.create_chessboard_graphviz_file()
        colours = self.__generate_distinct_colors__(len(paths))
        for i, path in enumerate(paths):
            if len(path) <= 0: 
                continue

            curr = path[0]
            for elem in path[1:]:
                start = f'{curr[0]},{curr[1]}'
                end = f'{elem[0]},{elem[1]}'
                self.dot.edge(start, end, color=colours[i])
                curr = elem

    def save_graphviz(self):
        """
        Utility function for saving the graphviz file
        """
        if self.dot is None: 
            self.create_chessboard_graphviz_file()
        if not os.path.exists("graphviz_output"):
            os.mkdir("graphviz_output")
        self.dot.render(os.path.join("graphviz_output", "checkboard_solution.dot"), view=False)

    def __generate_distinct_colors__(self, n: int) -> List:
        """ 
        Generate n distinct RGB colors in hexadecimal format. 
        """
        colors = []
        for i in range(n):
            hue = i / n  # Vary hue between 0 and 1.
            saturation = 0.7  # Fixed saturation.
            value = 0.9  # Fixed value.
            rgb_fractional = colorsys.hsv_to_rgb(hue, saturation, value)
            rgb = [int(x * 255) for x in rgb_fractional]
            colors.append(f'#{rgb[0]:2x}{rgb[1]:2x}{rgb[2]:2x}')
        return colors

# Abstract piece in case we want to include other possible pieces
class Piece:
    """
    Piece abstract class for implementing future pieces
    """

    @abstractmethod
    def allowed_actions(self, point: Tuple[int, int], checkboard: Checkboard) -> Iterator[Tuple[Tuple, int]]:
        """
        Return generator of allowed actions as (Tuple, Int), where int is a weigth
        :param point: Starting cell
        :param checkboard: Checkboard used for boundaries check
        """

# Knight piece
class Knight(Piece):
    """
    Knight class
    """

    def allowed_actions(self, point: Tuple[int, int], checkboard: Checkboard) -> Iterator[Tuple[Tuple, int]]:
        row, col = point
        # A knight can move in an L manner, incresing his col/row by 2 and the row/col by 1
        for x, y in chain(product([2,-2], [1,-1]), product([1,-1], [2,-2])):
            if row + x >= 0 and row + x < checkboard.width and col+y >= 0 and col+y < checkboard.length:
                yield (row+x, col+y), 1
 
# Abstract Solving Algorithm in case we want to include possible future algorithms
class SolvingAlgorithm:
    """
    Abstract Solving Algorithm class for modelling a generic algorithm
    """
    
    def execute(self, *arg, **kwargs) -> Tuple[Set, float]:
        """
        Execute the Solving Algorithm and times it
        :return: A tuple of shortest paths and the time
        """
        return self._timed_logic(*arg, **kwargs)
    
    @timeit
    def _timed_logic(self, *arg, **kwargs) -> Tuple[Set, float]:
        """
        Custom internal function to apply the decorator
        :return: A tuple of shortest paths and the time
        """
        return self.logic(*arg, **kwargs)
    
    @abstractmethod
    def logic(self, *arg, **args) -> Set:
        """
        Function representing the algorithm logic
        :return: Set of shortest paths
        """


# Since the weight of moving from (rxc) to (r'xc') is equal to the length
# BFS can be used here because the weight is just the single move, that is the graph is unweighted.
class BFS(SolvingAlgorithm):
    """
    Breadth First Search Algorithm configured to search all shortest paths
    """

    # Class for storing parents in a more convenient way
    class PointVisited:
        """
        Class for modelling a point visited in a more compact way
        """

        def __init__(self, level: int):
            """
            :params level: "Move" number of the point
            """
            # List of parents of the child
            self.parents = []
            # Level of the point
            self.level = level

        def increase_level(self):
            """
            Increase number of moves
            """
            self.level += 1

        def add_parent(self, cell: Tuple[int, int]):
            """
            Add parent to the list of parents
            """
            self.parents.append(cell)

    def _is_same_level_(self, visited_points: Dict, child: Tuple[int, int], parent: Tuple[int, int]) -> bool:
        """
        Check if child's parent are at the same level of parent. Allows to consider multiple shortest paths.
        :param child: child cell
        :param parent: parent cell
        :return: boolean indicating if parent is at the same level of child
        """
        assert parent in visited_points and child in visited_points
        parent_stat = visited_points[parent]
        child_stat = visited_points[child]
        return any(parent_stat.level == visited_points[child_parent].level for child_parent in child_stat.parents)

    def logic(self, checkboard: Checkboard, piece: Piece, starting_point: Tuple[int, int], target_point: Tuple[int, int]) -> Set:
        """
        Logic function for the BTS

        :param checkboard: Checkboard which is passed to the piece
        :param starting_point: Point from which our piece start
        :param target_point: Point where which our piece should end
        :return: Set of shortest paths
        """
        visited_points = {starting_point: self.PointVisited(1)}
        point_to_visit = deque([starting_point])
        not_ended = True

        while len(point_to_visit) > 0: # All shortest paths
            # Extract the first cell to visit
            current_point = point_to_visit.popleft()
            current_stat = visited_points[current_point]
            # Check if the cell is the target one
            if Checkboard.are_points_equal(current_point, target_point):
                break
            # Schedule the visit of the points reachable from the knight based on the chosen strategy
            for visitable_pair in piece.allowed_actions(current_point, checkboard=checkboard):
                # Separate weight from point
                visitable_point, _ = visitable_pair
                # Check if point has been visited
                if visitable_point not in visited_points:
                    # Increase the distance of this cell
                    visited_points[visitable_point] = self.PointVisited(current_stat.level + 1)
                    # Append the visitable cell to the deque
                    if not_ended: 
                        point_to_visit.append(visitable_point)
                    # Trace path
                    visited_points[visitable_point].add_parent(current_point)
                # If visited, and this cell requires the same number of steps as our current cell
                # it means that the knight could use this cell to reach target in the same amount of steps
                elif self._is_same_level_(visited_points, visitable_point, current_point):
                    visited_points[visitable_point].add_parent(current_point)


        # Visited point contains the shortest paths. Reconstruct them.
        paths = set()
        # Stack like structure to visit the paths
        visit = [(target_point, [target_point])]

        while len(visit) > 0:
            # Get current point and path
            curr_point, curr_path = visit.pop()
            # If curr_point is the starting_point, add path
            if curr_point == starting_point:
                paths.add(tuple(curr_path))
            # Check if the point is in the visited cells
            if curr_point in visited_points:
                # Retrieve the parents
                parents = visited_points[curr_point].parents
                for parent in parents:
                    visit.append((parent, curr_path + [parent]))

        # Register paths, reverting them
        paths = {path[::-1] for path in paths}
        return paths
        
#################################
#            MAIN               #
#################################

def check_single_param(element: int, info: str, max_allowed: int, min_allowed = 0) -> bool:
    """
    Checking if a parameter conforms to constraint

    :param element: element to check
    :param info: message to output
    :param max_allowed: upperbound
    :param min_allowed: lowerbound, defaults to 0
    :return: a boolean
    """
    if element >= max_allowed or element < min_allowed:
        print(f"[PARAMETER ERROR] {info} provided is not within bounds. Value: {element}, max allowed: {max_allowed-1}, min allowed: {min_allowed}")
        return False
    return True

def check_params(row: int, col: int, t_r: int, t_c: int, bw: int, bl: int):
    """
    Check if all parameters are within bounds
    """
    if bw < 0 or bl < 0: 
        print(f"[PARAMETER ERROR] Provided negative checkboard width/length. Width: {bw}, Length: {bl}")
        return False
    # all is used here WITHOUT generator to evaluate all the parameters
    return all([check_single_param(r, i, m) for r,i,m in zip([row, col, t_r, t_c], ["Row", "Column", "Target_Row", "Target_Column"], [bw, bl, bw, bl])])

def knight_simulation(row: int, col: int, t_r: int, t_c: int, bw: int, bl: int):
    """ 
    Function that, given two points P and P', returns the shortest paths from P to P'
    :param row: Row of the starting point P
    :param col: Column of the starting point P'
    :param t_r: Row of the target point P
    :param t_c: Column of the target point P'
    :param bw: Width of the checkboard (default 8)
    :param bl: Length of the checkboard (default 8)
    :return: Set of shortest paths + saves a graph file
    """
    checkboard = Checkboard(bw, bl)
    piece = Knight()
    algorithm = BFS()

    paths, elapsed_time = algorithm.execute(checkboard, piece, (row,col), (t_r, t_c))
    checkboard.add_paths_to_graphviz(paths)
    checkboard.save_graphviz()
    print("[INFO] Terminated.")
    print("[RESULTS]")
    print("- Paths:", paths)
    print("- Number of paths:", len(paths))
    print("- Execution Time:", elapsed_time)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Take two position on a checkboard (default 8x8) and output the set of shortest paths.")
    
    parser.add_argument("row", help="Row of the checkboard. Must be 0 <= row < MAX_WIDTH (default = 8)", type=int)
    parser.add_argument("column", help="Column of the checkboard. Must be 0 <= column < MAX_LENGTH (default = 8)", type=int)
    parser.add_argument("target_row", help="Target Row of the checkboard. Must be 0 <= row < MAX_WIDTH (default = 8)", type=int)
    parser.add_argument("target_column", help="Target Column of the checkboard. Must be 0 <= column < MAX_LENGTH (default = 8)", type=int)
    parser.add_argument("-bw", "--board_width", help="Custom width of the checkboard", default=MAX_WIDTH, type=int)
    parser.add_argument("-bl", "--board_length", help="Custom length of the checkboard", default=MAX_LENGTH, type=int)

    # Parse the arguments
    args = parser.parse_args()

    row = args.row
    column = args.column
    target_row = args.target_row
    target_column = args.target_column
    board_width = args.board_width if args.board_width is not None else MAX_WIDTH
    board_length = args.board_length if args.board_length is not None else MAX_LENGTH

    # Check validity of points
    if not check_params(row, column, target_row, target_column, board_width, board_length):
        print("[PROGRAM ERROR] At least one provided parameter is not valid.")
        sys.exit()

    knight_simulation(row, column, target_row, target_column, board_width, board_length)
