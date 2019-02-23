"""
A collection of implementations of the Player class
Maybe these should be separated into their own files?
"""

import random
import itertools
from abc import ABC, abstractmethod
from math import inf
from board import SWAP_MOVE

# a player interface
class Player(ABC):
    def __init__(self, player_num):
        super(Player, self).__init__()
        self.player_num = player_num

    # gives the player a board state, and asks them to make a move
    @abstractmethod
    def move(self, board):
        pass

    # an easy way to tell if the player is one of the human types
    @abstractmethod
    def is_human(self):
        pass


# abstract classes to keep behaviour common to all humans or bots
class HumanPlayer(Player, ABC):
    def is_human(self):
        return True


class ComputerPlayer(Player, ABC):
    def is_human(self):
        return False


class TextPlayer(HumanPlayer):
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

class RandomPlayer(ComputerPlayer):
    def move(self, board):
        options = [(y, x) for (y, x) in itertools.product(range(board.size), repeat=2) if board[y][x] == 0]
        if board.swap_rule and len(board.move_list) == 1:
            options.append(board.move_list[0])
        move = random.choice(options)
        board.play(*move)

# uses bounded min-max tree search with alpha beta pruning
minimax_search_depth = 3
class AlphaBetaPlayer(ComputerPlayer):
    def __init__(self, player_num, use_heuristic_sort):
        super(AlphaBetaPlayer, self).__init__(player_num)
        self.use_heuristic_sort = use_heuristic_sort

    @staticmethod
    def heuristic(board):
        if board.winner != 0:
            # player 1 gives inf, player 2 gives -inf
            return (3-2*board.winner)*inf
        else:
            # find the player that's closer to winning
            p1_dist, _ = board.remaining_distance(1)
            p2_dist, _ = board.remaining_distance(2)
            return p2_dist - p1_dist

    def move(self, board):
        val, move = self.alpha_beta(board, minimax_search_depth, -inf, inf, self.player_num)
        print(val)
        if move is None:
            board.resign()
        else:
            board.play(*move)

    def alpha_beta(self, board, depth, alpha, beta, player, states=None):
        if states is None:
            states = dict()
        if depth == 0 or board.winner != 0:
            # if we've reached the end, there is no move to make
            return self.heuristic(board), None

        # make a generator for all options
        options = [(y, x) for (y, x) in itertools.product(range(board.size), repeat=2) if board[y][x] == 0]
        if board.swap_rule and len(board.move_list) == 1:
            # options = itertools.chain((board.move_list[0],),options)
            options.append(SWAP_MOVE)

        if self.use_heuristic_sort:
            curve_board = ChargeHeuristicPlayer.curve_board(board)
            options.sort(key=lambda m: 0 if m == SWAP_MOVE else curve_board[m[0]][m[1]])

        # player 1 tries to maximize the board value, player 2 tries to minimize it
        value = -inf if player == 1 else inf
        best_move = None
        for move in options:
            board.play(*move)
            board_state = board.hashable()
            if board_state in states:
                move_val = states[board_state]
            else:
                move_val, _ = self.alpha_beta(board, depth-1, alpha, beta, 3-player, states=states)
                states[board_state] = move_val
            if player == 1:
                if move_val > value:
                    value = move_val
                    best_move = move
                alpha = max(alpha, value)
            else:
                if move_val < value:
                    value = move_val
                    best_move = move
                beta = min(beta, value)
            board.undo()
            if alpha >= beta:
                break
        return value, best_move


# this player is a mess. They try to find "saddle points" in the distance function
# on the board to signify that
_max_charge = 9
class ChargeHeuristicPlayer(ComputerPlayer):

    @staticmethod
    def base_charge(size):
        base = [[0]*(size+2) for y in range(size+2)]
        # treat the end zones as lines of charge
        for i in range(size):
            ChargeHeuristicPlayer.add_charge(1, base, -1, i)
            ChargeHeuristicPlayer.add_charge(1, base, size, i)
            ChargeHeuristicPlayer.add_charge(-1, base, i, -1)
            ChargeHeuristicPlayer.add_charge(-1, base, i, size)
        return base

    @staticmethod
    def distance(x1, y1, x2, y2):
        manhattan = abs(x2-x1)+abs(y2-y1)
        diagonal = abs(x2-x1)+abs(y2-y1+(x2-x1))
        return min(manhattan, diagonal)

    @staticmethod
    def add_charge(sign, charge, x, y):
        x += 1
        y += 1
        for y2, x2 in itertools.product(range(len(charge)), repeat=2):
            if abs(charge[y2][x2]) == _max_charge:
                continue
            if (y2, x2) == (y, x):
                charge[y2][x2] = sign * _max_charge
            else:
                charge[y2][x2] += sign * (1 / ChargeHeuristicPlayer.distance(x,y,x2,y2) ** 2)
            charge[y2][x2] = max(min(charge[y2][x2], _max_charge), -_max_charge)

    @staticmethod
    def inverse_radius(h1,h2,h3):
        # simplified equation for finding the radius of a circle defined by 3 points
        # I've changed it a lot because I don't actually care about the number, just the relationship between numbers
        a = (1 + ((h1 - h2)/4/_max_charge) ** 2)
        b = (1 + ((h3 - h2)/4/_max_charge) ** 2)
        c = (4 + ((h1 - h3)/4/_max_charge) ** 2)
        area = (h3-2*h2+h1)
        return area/(a*b*c)

    @staticmethod
    def curve(h1, h2, h3):
        # return ChargeHeuristicPlayer.inverse_radius(h1,h2,h3)
        if min(h1,h2,h3) == h2 or max(h1,h2,h3) == h2:
            # upwards or downwards curve
            return (h1-h2)+(h3-h2)
        else:
            # other curved shapes are not evaluatable
            return 0

    @staticmethod
    def curve_board(board):
        charge = ChargeHeuristicPlayer.base_charge(board.size)
        for y, x in itertools.product(range(board.size), repeat=2):
            if board[y][x] != 0:
                sign = 1 if board[y][x] == 1 else -1
                ChargeHeuristicPlayer.add_charge(sign, charge, x, y)
        # for row in charge:
        #     print(list((('%.4f'%x) if x >= 0 else ('%.3f'%x) for x in row)))
        curve = [[0]*board.size for i in range(board.size)]
        for y, x in itertools.product(range(1,board.size+1), repeat=2):
            k_e_w = ChargeHeuristicPlayer.curve(charge[y][x-1], charge[y][x], charge[y][x+1])
            k_ne_sw = ChargeHeuristicPlayer.curve(charge[y+1][x-1], charge[y][x], charge[y-1][x+1])
            k_nw_se = ChargeHeuristicPlayer.curve(charge[y+1][x], charge[y][x], charge[y-1][x])
            curve[y-1][x-1] = min(k_e_w, k_ne_sw, k_nw_se) * max(k_e_w, k_ne_sw, k_nw_se)
            # print('%.3f'%curve[y-1][x-1], end=',' if x < board.size else '\n')
        return curve

    def move(self, board):
        curve = ChargeHeuristicPlayer.curve_board(board)
        move = (-1, -1)
        move_curvature = inf
        for y, x in itertools.product(range(0,board.size), repeat=2):
            if curve[y][x] < move_curvature and board[y][x] == 0:
                move = (y,x)
                move_curvature = curve[y][x]
        board.play(*move)
