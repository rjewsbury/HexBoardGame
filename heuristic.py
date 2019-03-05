"""
A collection of heuristic functions,
used by players to evaluate board positions
"""
import itertools
from abc import ABC, abstractmethod
from copy import deepcopy
from math import inf


class Heuristic(ABC):
    # gets the value of a given board state
    # if a player has won, the board value is maximally positive or negative
    def get_value(self, board):
        # either the positive player or negative player won
        if board.winner != 0:
            return board.winner * inf
        else:
            return 0

    # gets an array of heuristic values for every position on the board
    # intended to be used to sort options
    def get_child_values(self, board):
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


class ShortestPathHeuristic(Heuristic):
    def get_value(self, board):
        if board.winner != 0:
            return board.winner * inf
        else:
            # find the player that's closer to winning
            p1_dist, _ = board.remaining_distance(1)
            p2_dist, _ = board.remaining_distance(-1)
            return p2_dist - p1_dist


class ChargeHeuristic(Heuristic):
    _max_charge = 9

    def __init__(self, size):
        super(ABC, self).__init__()
        self._base_charge = self.base_charge(size)
        self.size = size

    # finds an approximation of "curvature" if the board was an electric field
    def get_child_values(self, board):
        charge = deepcopy(self._base_charge)
        for y, x in itertools.product(range(board.size), repeat=2):
            if board[y][x] != 0:
                sign = 1 if board[y][x] == 1 else -1
                ChargeHeuristic.add_charge(sign, charge, x, y)
        # for row in charge:
        #     print(list((('%.4f'%x) if x >= 0 else ('%.3f'%x) for x in row)))
        curve = [[0] * board.size for i in range(board.size)]
        for y, x in itertools.product(range(1, board.size + 1), repeat=2):
            k_e_w = ChargeHeuristic.curve(charge[y][x - 1], charge[y][x], charge[y][x + 1])
            k_ne_sw = ChargeHeuristic.curve(charge[y + 1][x - 1], charge[y][x], charge[y - 1][x + 1])
            k_nw_se = ChargeHeuristic.curve(charge[y + 1][x], charge[y][x], charge[y - 1][x])
            curve[y - 1][x - 1] = min(k_e_w, k_ne_sw, k_nw_se) * max(k_e_w, k_ne_sw, k_nw_se)
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
