"""
A collection of implementations of the Player class
Maybe these should be separated into their own files?
"""

import random
import itertools
from abc import ABC, abstractmethod
from math import inf
from board import SWAP_MOVE
from heuristic import ChargeHeuristic, ShortestPathHeuristic


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
class AlphaBetaPlayer(ComputerPlayer):
    def __init__(self, player_num, board_size, search_depth, use_heuristic_sort):
        super(AlphaBetaPlayer, self).__init__(player_num)
        self.search_depth = search_depth
        self.transposition_table = None
        self.heuristic = ShortestPathHeuristic()
        if use_heuristic_sort:
            self.sorter = ChargeHeuristic(board_size)
        else:
            self.sorter = None

    def move(self, board):
        # clear the transposition table from the previous search, because the new table will use deeper values
        self.transposition_table = dict()
        val, move = self.alpha_beta(board, self.search_depth, -inf, inf, self.player_num)
        print(val)
        if move is None:
            board.resign()
        else:
            board.play(*move)

    def alpha_beta(self, board, depth, alpha, beta, player):
        if depth == 0 or board.winner != 0:
            # if we've reached the end, there is no move to make
            return self.heuristic.get_value(board), None

        # make a generator for all options
        options = [(y, x) for (y, x) in itertools.product(range(board.size), repeat=2) if board[y][x] == 0]
        if board.swap_rule and len(board.move_list) == 1:
            # options = itertools.chain((board.move_list[0],),options)
            options.append(SWAP_MOVE)

        # by default, the algorithm searches top-left to bottom-right. if we use a fast heuristic to sort the options,
        # it can try to find moves that will result in cut-offs early
        if self.sorter is not None:
            child_val = self.sorter.get_child_values(board)
            options.sort(key=lambda m: 0 if m == SWAP_MOVE else child_val[m[0]][m[1]])

        # player 1 tries to maximize the board value, player 2 tries to minimize it
        value = -inf if player == 1 else inf
        best_move = None
        for move in options:
            board.play(*move)
            board_state = board.hashable()
            if board_state in self.transposition_table:
                move_val = self.transposition_table[board_state]
            else:
                move_val, _ = self.alpha_beta(board, depth-1, alpha, beta, 3-player)
                self.transposition_table[board_state] = move_val
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
class ChargeHeuristicPlayer(ComputerPlayer):
    def __init__(self, player_num, board_size):
        super(ChargeHeuristicPlayer, self).__init__(player_num)
        self.heuristic = ChargeHeuristic(board_size)

    def move(self, board):
        curve = self.heuristic.get_child_values(board)
        move = (-1, -1)
        move_curvature = inf
        for y, x in itertools.product(range(0,board.size), repeat=2):
            if curve[y][x] < move_curvature and board[y][x] == 0:
                move = (y,x)
                move_curvature = curve[y][x]
        board.play(*move)
