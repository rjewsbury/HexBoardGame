import random
import itertools
from abc import ABC, abstractmethod
from math import inf


# a player interface
class Player(ABC):
    # gives the player a board state, and asks them to make a move
    @abstractmethod
    def move(self, board):
        pass

    # an easy way to tell if the player is one of the human types
    @abstractmethod
    def is_human(self):
        pass


class TextPlayer(Player):
    def __init__(self, player_id=0):
        self.player_id = player_id

    def move(self, board):
        user = input('row, col (or "resign"/"undo"): ')
        try:
            row, col = (int(i) - 1 for i in user.split(','))
            board.play(row, col)
        except ValueError:
            if user == 'resign':
                board.resign()
            elif user == 'undo':
                board.undo()
                board.undo()

    def is_human(self):
        return True


class RandomPlayer(Player):
    def move(self, board):
        options = [(y, x) for (y, x) in itertools.product(range(board.size), repeat=2) if board[y][x] == 0]
        if board.swap_rule and len(board.move_list) == 1:
            options.append(board.move_list[0])
        move = random.choice(options)
        board.play(*move)

    def is_human(self):
        return False

# _max_charge = 10
# class ChargeHeuristicPlayer(Player):
#     def base_charge(self, size):
#         return [[1 / (x + 1) + 1 / (size - x) - 1 / (y + 1) - 1 / (size - y) for x in range(size)] + [_max_charge]
#                 for y in range(size)] + [[-_max_charge] * size + [0]]
#
#     def center_point(self,p1,p2,p3):
#         return 0,0
#
#     def move(self, board):
#         charge = self.base_charge(board.size)
#         for y1, x1 in itertools.product(range(board.size), repeat=2):
#             if board[y1][x1] != 0:
#                 sign = 3 - 2 * board[y1][x1]
#                 for y2, x2 in itertools.product(range(board.size), repeat=2):
#                     if (y2, x2) == (y1, x1):
#                         charge[y2][x2] += sign * _max_charge
#                     else:
#                         charge[y2][x2] += sign * (1 / ((y2 - y1) ** 2 + (x2 - x1 + (y2 - y1)/2) ** 2))
#         move = (-1, -1)
#         move_curvature = inf
#         for y, x in itertools.product(range(board.size), repeat=2):
#             c_e_w = self.center_point((-1,charge[y][x-1]), (0, charge))
#             k_e_w =
#             k_ne_sw = 0
#             k_nw_se = 0
#
#     def is_human(self):
#         return False
