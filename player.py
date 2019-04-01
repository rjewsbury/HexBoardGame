"""
A collection of implementations of the Player class
Maybe these should be separated into their own files?
"""

import random
import itertools
from abc import ABC, abstractmethod
from math import inf
from timeit import default_timer

from board import SWAP_MOVE
from heuristic import ChargeHeuristic


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


class GuiPlayer(HumanPlayer):
    def set_gui(self, gui):
        self.gui = gui

    def move(self, board):
        move = self.gui.get_move(self.player_num)
        if move == 'resign':
            board.resign()
            self.gui.reset_move()
        elif move == 'undo':
            board.undo()
            board.undo()
            self.gui.reset_move()
        elif move is not None:
            board.play(*move)
            self.gui.reset_move()


class RandomPlayer(ComputerPlayer):
    def move(self, board):
        options = [(y, x) for (y, x) in itertools.product(range(board.size), repeat=2) if board[y][x] == 0]
        if board.swap_rule and len(board.move_list) == 1:
            options.append(board.move_list[0])
        move = random.choice(options)
        board.play(*move)


# uses bounded min-max tree search with alpha beta pruning
class AlphaBetaPlayer(ComputerPlayer):
    def __init__(self, player_num, heuristic, search_depth=-1, max_time=0, sorter=None, killer_moves=6):
        super(AlphaBetaPlayer, self).__init__(player_num)
        # the number of moves deep to search in the tree
        self.search_depth = search_depth
        # the amount of time given for iterative deepening. only used when search_depth < 0
        self.max_time = max_time
        # the heuristic function used to evaluate leaf nodes
        self.heuristic = heuristic
        # the sorting function used to determine which branch to search first
        self.sorter = sorter
        # the number of cutoff moves to remember at each depth
        self.killer_moves = killer_moves

        if search_depth < 0 and max_time <= 0:
            raise ValueError('AlphaBetaPlayer needs either a search_depth, or a max_time')

    def move(self, board):
        transposition_table = dict()
        if self.search_depth < 0:
            val, move_list = self.iterative_deepening(board, self.max_time)
        else:
            val, move_list, time_up = self.alpha_beta(board, self.search_depth, -inf, inf, self.player_num, transposition_table, sorter=self.sorter)
            # val, move_list = self.MTD_f(board, self.heuristic.get_value(board)+self.player_num, self.search_depth

        print('expected value:', val)
        print('expected moves:', move_list)

        # if the game seems lost, resign
        if move_list is None or val*self.player_num < -100:
            board.resign()
        else:
            board.play(*(move_list[0]))

    def alpha_beta(self, board, depth, alpha, beta, player, transposition_table,
                   killer_moves=None, sorter=None, start_time=None, max_time=None):
        if killer_moves is None:
            killer_moves = [[(board.size//2,board.size//2)]*self.killer_moves for _ in range(depth+1)]
        elif len(killer_moves) < depth:
            killer_moves.extend(([(board.size//2,board.size//2)]*self.killer_moves for _ in range(depth+1-len(killer_moves))))

        if depth == 0 or board.winner != 0:
            # if we've reached the end, there is no move to make
            return self.heuristic.get_value(board), None, False

        # make a generator for all options
        options = [(y, x) for (y, x) in itertools.product(range(board.size), repeat=2) if board[y][x] == 0]
        if board.swap_rule and len(board.move_list) == 1:
            # options = itertools.chain((board.move_list[0],),options)
            options.append(SWAP_MOVE)

        # by default, the algorithm searches top-left to bottom-right. if we use a fast heuristic to sort the options,
        # it can try to find moves that will result in cut-offs early
        if sorter is not None:
            child_val = sorter.get_child_values(board)
            options.sort(key=lambda m: 0 if m == SWAP_MOVE else child_val[m[0]][m[1]])

        options = itertools.chain(killer_moves[depth], options)
        searched = set()

        # player 1 tries to maximize the board value, player 2 tries to minimize it
        value = -inf if player == 1 else inf
        best_move = None
        time_up = False
        for move in options:
            if board[move[0]][move[1]] != 0 or move in searched:
                continue
            searched.add(move)
            board.play(*move)
            board_state = board.hashable()
            if transposition_table is not None:
                if board_state in transposition_table:
                    move_val, move_list = transposition_table[board_state]
                else:
                    move_val, move_list, time_up =\
                        self.alpha_beta(board, depth-1, alpha, beta, -player, transposition_table,
                                        killer_moves=killer_moves, sorter=sorter, start_time=start_time, max_time=max_time)
                    if not time_up:
                        transposition_table[board_state] = (move_val, move_list)
            else:
                move_val, move_list, time_up = self.alpha_beta(board, depth-1, alpha, beta, -player, transposition_table,
                                                               killer_moves, sorter, start_time, max_time)
            board.undo()

            # if we didnt run out of time, we successfully explored this branch
            if not time_up:
                if player > 0:
                    if move_val > value:
                        value = move_val
                        best_move = (move, move_list)
                    alpha = max(alpha, value)
                else:
                    if move_val < value:
                        value = move_val
                        best_move = (move, move_list)
                    beta = min(beta, value)
                # if we've found a better move, we can do a cutoff
                if alpha >= beta:
                    # record the move that caused the cutoff
                    if move not in killer_moves[depth]:
                        killer_moves[depth].append(move)
                        killer_moves[depth].pop(0)
                    break
            # if we've run out of time, we need to get out of this tree search
            if max_time and (time_up or (default_timer() - start_time > max_time)):
                time_up = True
                break
        return value, best_move, time_up

    def iterative_deepening(self, board, max_time):
        start_time = default_timer()
        sorter = self.sorter
        depth = 1
        val = 0
        move_list = None
        time_up = False
        while not time_up:
            transposition_table = dict()
            next_val, next_move_list, time_up = self.alpha_beta(board, depth, -inf, inf, self.player_num, transposition_table,
                                             sorter=sorter, start_time=start_time, max_time=max_time)
            print('depth',depth,'value',next_val,'moves',next_move_list, 'time up',time_up)

            # if the search at this depth actually completed, record the result
            # keeping results of partial searches may lead to strange moves
            if not time_up:
                val = next_val
                move_list = next_move_list
                # print(transposition_table.values())
                depth += 1
            # if we've already used the majority of our time, we wont have time to complete another iteration
            if (default_timer() - start_time) / (max_time) > 0.5:
                time_up = True
        print('depth reached:',(depth-1))
        return val, move_list

    # a supposed efficiency improvement on the minimax search algorithm that uses 0-width alpha beta calls
    # makes the players choose different moves than regular alpha-beta depending on the initial guess?
    # might not use.
    def MTD_f(self, board, guess, depth):
        upper = inf
        lower = -inf
        val = guess
        move_list = None
        while lower < upper:
            bound = max(val, lower + 1)
            transposition_table = dict()
            val, move_list, time_up = self.alpha_beta(board, depth, bound - 1, bound, self.player_num, transposition_table)
            if val < bound:
                upper = val
            else:
                lower = val
        return val, move_list


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
