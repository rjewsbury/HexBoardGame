"""
A collection of heuristic functions,
used by players to evaluate board positions
"""
import itertools
import math
from abc import ABC
from copy import deepcopy
from heapq import heappush, heappop
from math import inf

from board import SWAP_MOVE, ADJACENT


# a heuristic interface
class Heuristic(ABC):
    # gets the value of a given board state
    # if a player has won, the board value is maximally positive or negative
    def get_value(self, board, debug=False):
        # either the positive player or negative player won
        if board.winner != 0:
            return board.winner * inf
        else:
            return 0

    # gets an array of heuristic values for every position on the board
    # intended to be used to sort options
    def get_child_values(self, board, debug=False):
        # if the game is over, no moves can be made
        if board.winner != 0:
            value = self.get_value(board)
            return [[value] * board.size for _ in range(board.size)]
        # otherwise, try every legal move
        heuristic = [[0] * board.size for _ in range(board.size)]
        for i,j in itertools.product(range(board.size), repeat=2):
            if board[i][j] == 0:
                board.play(i,j)
                heuristic[i][j] = self.get_value(board)
                board.undo()
        return heuristic


# finds out which player has fewer moves remaining
# in the shortest straight-line path across the board
class ShortestPathHeuristic(Heuristic):
    def get_value(self, board, debug=False):
        if board.winner != 0:
            return board.winner * inf
        else:
            # find the player that's closer to winning
            p1_dist = self.shortest_distance(board, 1, debug)
            p2_dist = self.shortest_distance(board, -1, debug)
            return p2_dist - p1_dist

    def shortest_distance(self, board, player, debug=False):
        # search ordered by min distance, intended direction
        if player == 1:
            searchq = [(0, board.size, i, board.size) for i in range(board.size-1)]
        else:
            searchq = [(0, board.size, board.size, i) for i in range(board.size - 1)]
        if debug: dist_grid = [['-'] * board.size for _ in range(board.size)]
        # the open set for adjacent cells
        searched = set()
        # track the distance travelled
        dist = -1
        # track the last cell visited
        row, col = -1, -1
        connected = False
        while searchq:
            dist, weight, row, col = heappop(searchq)

            # if the main axis is at 0, we've crossed the whole board
            if weight == 0:
                connected = True
                break
            for dy, dx in ADJACENT:
                next_row = row + dy
                next_col = col + dx

                # efficiency optimization. faster than checking if the cell is out of bounds
                try:
                    if next_row < 0 or next_col < 0:
                        continue
                    else:
                        board_val = board.board[next_row][next_col]
                except IndexError:
                    # if the position is not a legal board position, move on. faster than calling in-bounds
                    continue
                # if we can extend to the cell, add it to the search queue
                if board_val == player and (next_row, next_col) not in searched:
                    searched.add((next_row, next_col))
                    heappush(searchq, (dist, next_col if player == 1 else next_row, next_row, next_col))
                    if debug: dist_grid[next_row][next_col] = '0123456789ABCDEFGHIJKLMNOP'[dist]
                # unoccupied cells increase the distance
                elif board_val == 0 and (next_row, next_col) not in searched:
                    searched.add((next_row, next_col))
                    heappush(searchq, (dist + 1, next_col if player == 1 else next_row, next_row, next_col))
                    if debug: dist_grid[next_row][next_col] = '0123456789ABCDEFGHIJKLMNOP'[dist + 1]

        if debug: board.pretty_print(chars=dist_grid)
        if connected:
            return dist
        # if there is no way to reach the other side, treat it as infinite distance
        else:
            return inf


# finds out which player has the shorter remaining path using "Two Distance"
# which picks the second best options as it moves across the board
class TwoDistanceHeuristic(Heuristic):
    def get_value(self, board, debug=False):
        if board.winner != 0:
            return board.winner * inf
        else:
            # find the player that's closer to winning
            p1_dist = self.two_distance(board, 1, debug=debug)
            p2_dist = self.two_distance(board, -1, debug=debug)
            val = p2_dist - p1_dist
            # if a player does not have a 2-distance path, pick a high finite number, so we dont confuse it with a
            # definite win or a definite loss
            if math.isinf(val):
                val = int(math.copysign(100, val))
                fallback = ShortestPathHeuristic()
                val += fallback.get_value(board)
            if math.isnan(val):
                # if neither player has a path to their opposite side, we get nan
                # in this rare case, revert to normal distance
                fallback = ShortestPathHeuristic()
                val = fallback.get_value(board)
            return val

    def two_distance(self, board, player, debug=False):
        # search ordered by min distance, intended direction, then perpendicular direction
        if player == 1:
            searchq = [(0, board.size, i, board.size, (i, board.size)) for i in range(-1, board.size)]
        else:
            searchq = [(0, board.size, board.size, i, (board.size, i)) for i in range(-1, board.size)]
        # the best cell adjacent to each cell on the board
        best_neighbor = [[None] * board.size for _ in range(board.size)]
        # the best cell that's adjacent to the opposite wall
        best_opposite = None
        if debug: dist_grid = [['-'] * board.size for _ in range(board.size)]
        # the open set for adjacent cells
        searched = set()
        # track the distance travelled
        dist = -1
        # track the last cell visited
        row, col = -1, -1
        connected = False
        while searchq:
            dist, weight, row, col, neighbor = heappop(searchq)

            # if the main axis is at 0, we've crossed the whole board
            if weight == 0:
                if best_opposite is None:
                    best_opposite = neighbor
                elif best_opposite != neighbor:
                    connected = True
                    break

            for dy, dx in ADJACENT:
                next_row = row + dy
                next_col = col + dx

                # efficiency optimization. faster than checking if the cell is out of bounds
                try:
                    if next_row < 0 or next_col < 0: continue
                    else: board_val = board.board[next_row][next_col]
                # if the position is not a legal board position, move on. faster than calling in-bounds
                except IndexError: continue

                if board_val == 0 and (next_row, next_col) not in searched:
                    if best_neighbor[next_row][next_col] is None:
                        best_neighbor[next_row][next_col] = neighbor
                    elif best_neighbor[next_row][next_col] != neighbor:
                        searched.add((next_row, next_col))
                        heappush(searchq, (dist + 1, next_col if player == 1 else next_row, next_row, next_col, (next_row, next_col)))
                        if debug: dist_grid[next_row][next_col] = '0123456789ABCDEFGHIJKLMNOP'[dist + 1]

                elif board_val == player and (next_row, next_col) not in searched:
                    if best_neighbor[next_row][next_col] is None:
                        best_neighbor[next_row][next_col] = neighbor
                        # we need to extend the neighborhood to the rest of the connected group
                        # even though *this* cell doesnt have two neighbors, one of the connected cells might
                        heappush(searchq, (dist, next_col if player == 1 else next_row, next_row, next_col, neighbor))
                    elif best_neighbor[next_row][next_col] != neighbor:
                        searched.add((next_row, next_col))
                        best_neighbor[next_row][next_col] = neighbor
                        heappush(searchq, (dist, next_col if player == 1 else next_row, next_row, next_col, neighbor))
                        if debug: dist_grid[next_row][next_col] = '0123456789ABCDEFGHIJKLMNOP'[dist + 1]

        if debug: board.pretty_print(chars=dist_grid)

        # once the search is finished, build the list of the shortest path
        if connected:
            return dist
        # if there is no way to reach the other side, treat it as infinite distance
        else:
            return inf


# unused class. Supposed to remember values from previous searches to aid search
class PastResultHeuristic(Heuristic):
    def __init__(self, results, fallback=None):
        self.results = results
        self.fallback = fallback

    def get_value(self, board, debug=False):
        board_hash = board.hashable()
        if board_hash in self.results:
            return self.results[board_hash][0]
        elif self.fallback:
            return self.fallback.get_value(board)
        else:
            return super(PastResultHeuristic, self).get_value(board)


# Treats stones as positive/negative charges, and tries to find sadle points in the field
# supposed to represent choosing contested moves
class ChargeHeuristic(Heuristic):
    _max_charge = 9

    def __init__(self, size):
        super(ABC, self).__init__()
        self._base_charge = self.base_charge(size)
        self.size = size
        self.states = []

    # finds an approximation of "curvature" if the board was an electric field
    def get_child_values(self, board, debug=False):
        same_moves = 0
        for move, state in zip(board.move_list, self.states):
            if move == state[0][-1]:
                same_moves += 1
        if same_moves == 0:
            charge = deepcopy(self._base_charge)
        else:
            charge = deepcopy(self.states[same_moves-1][1])
        # remove the incorrect values
        self.states = self.states[:same_moves]

        for i in range(same_moves, len(board.move_list)):
            y, x = board.move_list[i]
            # if they swapped, clear the board and mirror the first move
            if (y,x) == SWAP_MOVE:
                charge = deepcopy(self._base_charge)
                x, y = board.move_list[0]
            ChargeHeuristic.add_charge(board[y][x], charge, x, y)

            self.states.append((board.move_list[:i+1], charge))
            # copy the board so the one stored isnt modified
            if i+1 < len(board.move_list):
                charge = deepcopy(charge)

        # for row in charge:
        #     print(list((('%.4f'%x) if x >= 0 else ('%.3f'%x) for x in row)))
        curve = [[0] * board.size for i in range(board.size)]
        for y, x in itertools.product(range(1, board.size + 1), repeat=2):
            k_e_w = ChargeHeuristic.curve(charge[y][x - 1], charge[y][x], charge[y][x + 1])
            k_ne_sw = ChargeHeuristic.curve(charge[y + 1][x - 1], charge[y][x], charge[y - 1][x + 1])
            k_nw_se = ChargeHeuristic.curve(charge[y + 1][x], charge[y][x], charge[y - 1][x])
            curve[y - 1][x - 1] = min(k_e_w, k_ne_sw, k_nw_se) * max(k_e_w, k_ne_sw, k_nw_se)*-board.turn
            # print('%.3f'%curve[y-1][x-1], end=',' if x < board.size else '\n')
        return curve

    @staticmethod
    def base_charge(size):
        base = [[0] * (size + 2) for y in range(size + 2)]
        # treat the end zones as lines of charge
        for i in range(size):
            ChargeHeuristic.add_charge(1, base, -1, i)
            ChargeHeuristic.add_charge(1, base, size, i)
            ChargeHeuristic.add_charge(-1, base, i, -1)
            ChargeHeuristic.add_charge(-1, base, i, size)
        return base

    @staticmethod
    def distance(x1, y1, x2, y2):
        manhattan = abs(x2 - x1) + abs(y2 - y1)
        diagonal = abs(x2 - x1) + abs(y2 - y1 + (x2 - x1))
        return min(manhattan, diagonal)

    @staticmethod
    def add_charge(sign, charge, x, y):
        x += 1
        y += 1
        for y2, x2 in itertools.product(range(len(charge)), repeat=2):
            if abs(charge[y2][x2]) == ChargeHeuristic._max_charge:
                continue
            if (y2, x2) == (y, x):
                charge[y2][x2] = sign * ChargeHeuristic._max_charge
            else:
                charge[y2][x2] += sign * (1 / ChargeHeuristic.distance(x, y, x2, y2) ** 2)
            charge[y2][x2] = max(min(charge[y2][x2], ChargeHeuristic._max_charge), -ChargeHeuristic._max_charge)

    @staticmethod
    def inverse_radius(h1, h2, h3):
        # simplified equation for finding the radius of a circle defined by 3 points
        # I've changed it a lot because I don't actually care about the number, just the relationship between numbers
        a = (1 + ((h1 - h2) / 4 / ChargeHeuristic._max_charge) ** 2)
        b = (1 + ((h3 - h2) / 4 / ChargeHeuristic._max_charge) ** 2)
        c = (4 + ((h1 - h3) / 4 / ChargeHeuristic._max_charge) ** 2)
        area = (h3 - 2 * h2 + h1)
        return area / (a * b * c)

    @staticmethod
    def curve(h1, h2, h3):
        # return ChargeHeuristic.inverse_radius(h1,h2,h3)
        if min(h1, h2, h3) == h2 or max(h1, h2, h3) == h2:
            # upwards or downwards curve
            return (h1 - h2) + (h3 - h2)
        else:
            # other curved shapes are not evaluatable
            return 0
