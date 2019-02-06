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


_max_charge = 9
class ChargeHeuristicPlayer(Player):

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
            # curved slope
            return 0

    def move(self, board):
        charge = self.base_charge(board.size)
        for y, x in itertools.product(range(board.size), repeat=2):
            if board[y][x] != 0:
                sign = 1 if board[y][x] == 1 else -1
                ChargeHeuristicPlayer.add_charge(sign, charge, x,y)

        # for row in charge:
        #     print(list((('%.4f'%x) if x >= 0 else ('%.3f'%x) for x in row)))

        move = (-1, -1)
        move_curvature = inf
        for y, x in itertools.product(range(1,board.size+1), repeat=2):
            k_e_w = self.curve(charge[y][x-1], charge[y][x], charge[y][x+1])
            k_ne_sw = self.curve(charge[y+1][x-1], charge[y][x], charge[y-1][x+1])
            k_nw_se = self.curve(charge[y+1][x], charge[y][x], charge[y-1][x])
            curvature = min(k_e_w, k_ne_sw, k_nw_se) * max(k_e_w, k_ne_sw, k_nw_se)
            # print('%.3f'%curvature, end=',' if x < board.size else '\n')
            if curvature < move_curvature and board[y-1][x-1] == 0:
                move = (y-1,x-1)
                move_curvature = curvature
        board.play(*move)

    def is_human(self):
        return False
