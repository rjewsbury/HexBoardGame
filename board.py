"""
A data structure used to represent an arbitrary hex game state
"""
from math import inf
from heapq import heappop, heappush

# constants:
# the code used to represent a swap
SWAP_MOVE = (-1, -1)
# the list of directions that are connected to a stone
ADJACENT = [(-1, 0), (0, -1), (1, -1), (1, 0), (0, 1), (-1, 1)]


class HexBoard:
    def __init__(self, size=11, swap_rule=False):
        # the width and height of the board
        self.size = size
        # 0 means empty, 1 means a player 1 piece, -1 means a player 2 piece
        self.board = [[0] * size for _ in range(size)]
        # a rule that allows the second player to "swap places" as their first move
        self.swap_rule = swap_rule
        # a history of moves made.
        self.move_list = []
        # the player with the next move. either 1 or -1
        self.turn = 1
        # the player that's won the game
        self._winner = 0
        # the group of stones that connect the sides
        self._winning_group = None

    # for convenience, treat indexing on the hex board as indexing on the board itself
    def __getitem__(self, item):
        return self.board[item]

    # to use the board as a dictionary key, get its board state in a tuple
    def hashable(self):
        return tuple((tuple(row) for row in self.board))

    # treat the winner as a property so that it is only checked when we need to
    @property
    def winner(self):
        if self._winner is None:
            self._update_winner()
        return self._winner

    @property
    def winning_group(self):
        if self._winner is None:
            self._update_winner()
        return self._winning_group

    # checks if a given position is on the board
    def in_bounds(self, row, col):
        return (0 <= row < self.size) and (0 <= col < self.size)

    # if a move is valid, updates the board
    def play(self, row, col):
        moved = False

        # cant move if somebody already won
        if self.winner != 0:
            return moved

        # if there's no move there already, its valid
        if self.in_bounds(row, col) and self.board[row][col] is 0:
            self.board[row][col] = self.turn
            self.move_list.append((row, col))
            self.turn *= -1
            moved = True
            # in this new board state, we don't know if somebody's won
            self._winner = None

        # if swapping is allowed and it's player 2's first move, they can take player 1's first move
        elif self.swap_rule and len(self.move_list) == 1 and (
                        (row, col) == SWAP_MOVE or (row, col) == self.move_list[0]):
            # we mirror it across the board to make it seem like the players switched
            row, col = self.move_list[0]
            self.board[row][col] = 0
            self.board[col][row] = -1
            self.move_list.append(SWAP_MOVE)
            self.turn *= -1
            moved = True

        return moved

    # removes the most recent move
    def undo(self):
        # if the last move won, then we need to clear the result
        self._winner = 0
        self._winning_group = None
        self.turn *= -1
        row, col = self.move_list.pop()
        if (row, col) == SWAP_MOVE:
            row, col = self.move_list[0]
            self.board[col][row] = 0
            self.board[row][col] = 1
        else:
            self.board[row][col] = 0

    # sets the winner of the match
    def resign(self):
        self._winner = -self.turn

    # checks how much further a player has to go to connect.
    # if max is set, the search will stop early if the distance reaches max
    # if min_neighbors is set, nodes will only be searched if they have at least that many neighbors already searched
    def remaining_distance(self, player, max=0, min_neighbors=1, debug=False):
        # search ordered by min distance, intended direction, then perpendicular direction
        searchq = [(0, self.size, i) for i in range(-1,self.size)]
        neighbor_count = [[0]*self.size for _ in range(self.size)]
        if debug: dist_grid = [['-'] * self.size for _ in range(self.size)]
        # the open set for adjacent cells
        parent = dict()
        # track the distance travelled
        dist = -1
        # track the last cell visited
        row, col = -1, -1
        connected = False
        while searchq:
            dist, major, minor = heappop(searchq)

            if player == 1: # player 1 is travelling left-right, so the intended direction is the column number
                row, col = minor, major
            else:           # player 2 is travelling up-down, so the intended direction is the row number
                row, col = major, minor

            # if the main axis is at 0, we've crossed the whole board
            if major == 0:
                connected = True
                break

            # cut the search if we've reached the max
            if max and dist >= max:
                break
            for dy, dx in ADJACENT:
                next_row = row + dy
                next_col = col + dx

                # translate row/col to major/minor axis
                if player == 1:
                    major, minor = next_col, next_row
                else:
                    major, minor = next_row, next_col

                # efficiency optimization. faster than checking if the cell is out of bounds
                try:
                    if next_row < 0 or next_col < 0:
                        continue
                    else:
                        board_val = self.board[next_row][next_col]
                except IndexError:
                    # if the position is not a legal board position, move on. faster than calling in-bounds
                    continue

                # owned cells extend the neighborhood to the rest of the bordering cells
                if board_val == player and (next_row, next_col) not in parent:
                    parent[(next_row, next_col)] = (row, col)
                    heappush(searchq, (dist, major, minor))
                    if debug: dist_grid[next_row][next_col] = '0123456789ABCDEFGHIJKLMNOP'[dist]

                # empty cells need to consider neighbors
                elif board_val == 0 and (next_row, next_col) not in parent:
                    # if we're neighboring a claimed cell, we dont need to consider other neighbors
                    if row == self.size or col == self.size or self.board[row][col] == player:
                        neighbor_count[next_row][next_col] = inf
                    else:
                        neighbor_count[next_row][next_col] += 1

                    # if there are enough marked neighbors, we can search the cell
                    if neighbor_count[next_row][next_col] >= min_neighbors:
                        parent[(next_row, next_col)] = (row, col)
                        heappush(searchq, (dist+1, major, minor))
                        if debug: dist_grid[next_row][next_col] = '0123456789ABCDEFGHIJKLMNOP'[dist+1]

        if debug: self.pretty_print(chars=dist_grid)

        # once the search is finished, build the list of the shortest path
        if connected:
            pos = (row, col)
            winning_group = []
            while pos in parent:
                winning_group.append(pos)
                pos = parent[pos]
            return dist, winning_group
        # if the search ended because the max was exceeded, there is no winning group
        elif max and dist >= max:
            return dist, None
        # if there is no way to reach the other side, treat it as infinite distance
        else:
            return inf, None

    # checks if either player has won
    def _update_winner(self):
        disconnected, group = self.remaining_distance(1, max=1)
        if not disconnected:
            self._winner = 1
            self._winning_group = group
            return
        disconnected, group = self.remaining_distance(-1, max=1)
        if not disconnected:
            self._winner = -1
            self._winning_group = group
            return

        self._winner = 0
        self._winning_group = None

    def pretty_print(self, chars=None):
        # spacing should be odd for things to be consistent
        spacing = 3
        string = '\n' + ' ' * (2 + (spacing + 1) // 2)
        for i in range(self.size):
            string += ('{:' + str(spacing + 1) + '}').format(str(i + 1) + ':')
        string += '\n' + ' ' * (3 + (spacing + 1) // 2) + ('□' + ' ' * spacing) * self.size
        for i, row in enumerate(self.board):
            string += ('\n' + '{:>' + str(2 + i * (spacing + 1) // 2) + '} ■').format(str(i + 1) + ':')
            for j, num in enumerate(row):
                if self._winning_group and (i,j) in self._winning_group and (i,j-1) in self._winning_group:
                    string += ']' + ' ' * (spacing - 2) + '['
                elif self._winning_group and (i,j) in self._winning_group:
                    string += ' ' * (spacing - 1) + '['
                elif self._winning_group and (i,j-1) in self._winning_group:
                    string += ']' + ' ' * (spacing - 1)
                elif self.move_list and (self.move_list[-1] == (i,j) or
                        (self.move_list[-1] == SWAP_MOVE and self.move_list[-2] == (i,j))):
                    string += ' ' * (spacing - 1) + '('
                elif self.move_list and (self.move_list[-1] == (i,j-1) or
                        (self.move_list[-1] == SWAP_MOVE and self.move_list[-2] == (i,j-1))):
                    string += ')' + ' ' * (spacing - 1)
                else:
                    string += ' ' * spacing


                if num == 0:
                    if chars:
                        string += chars[i][j]
                    else:
                        string += '·'
                elif num < 0:
                    string += '○'
                else:
                    string += '●'
            if self._winning_group and (i,self.size-1) in self.winning_group:
                string += ']' + ' ' * (spacing-1)
            elif self.move_list and self.move_list[-1] == (i, self.size-1):
                string += ')' + ' ' * (spacing-1)
            else:
                string += ' ' * spacing
            string += '■'
        string += '\n' + ' ' * (4 + self.size * (spacing + 1) // 2) + (' ' * spacing + '□') * self.size
        print(string)
