# constants:
# the code used to represent a swap
SWAP_MOVE = (-1, -1)
# the list of directions that are connected to a stone
ADJACENT = [(-1, 0), (0, -1), (1, -1), (1, 0), (0, 1), (-1, 1)]


class HexBoard:
    def __init__(self, size=11, swap_rule=False):
        # the width and height of the board
        self.size = size
        # 0 means empty, 1 means a player 1 piece, 2 means a player 2 piece
        self.board = [[0] * size for _ in range(size)]
        # a rule that allows the second player to "swap places" as their first move
        self.swap_rule = swap_rule
        # a history of moves made.
        self.move_list = []
        # the player with the next move. either 1 or 2
        self.turn = 1
        # the player that's won the game
        self.winner = 0
        # the group of stones that connect the sides
        self.winning_group = None

    # for convenience, treat indexing on the hex board as indexing on the board itself
    def __getitem__(self, item):
        return self.board[item]

    # checks if a given position is on the board
    def in_bounds(self, row, col):
        return (0 <= row < self.size) and (0 <= col < self.size)

    # if a move is valid, updates the board
    def play(self, row, col):
        moved = False

        # cant move if somebody already won
        if self.winner > 0:
            return moved

        # if there's no move there already, its valid
        if self.in_bounds(row, col) and self.board[row][col] is 0:
            self.board[row][col] = self.turn
            self.move_list.append((row, col))
            self.turn = (self.turn % 2) + 1
            moved = True
            # check if somebody won
            self._update_winner()

        # if swapping is allowed and it's player 2's first move, they can take player 1's first move
        elif self.swap_rule and len(self.move_list) == 1 and (
                        (row, col) == SWAP_MOVE or (row, col) == self.move_list[0]):
            # we mirror it across the board to make it seem like the players switched
            row, col = self.move_list[0]
            self.board[row][col] = 0
            self.board[col][row] = 2
            self.move_list.append(SWAP_MOVE)
            self.turn = (self.turn % 2) + 1
            moved = True

        return moved

    def undo(self):
        self.winner = 0
        self.winning_group = None
        self.turn = (self.turn % 2) + 1
        row, col = self.move_list.pop()
        if (row, col) == SWAP_MOVE:
            row, col = self.move_list[0]
            self.board[col][row] = 0
            self.board[row][col] = 1
        else:
            self.board[row][col] = 0

    def resign(self):
        self.winner = (self.turn % 2) + 1

    def _update_winner(self):
        checked = [[False] * self.size for _ in range(self.size)]

        def connect_right(row, col):
            return col == self.size - 1

        # check for a player 1 win
        for row in range(self.size):
            # if a cell on the left is connected to the right side, player 1 wins
            connected, group = self._follow_connection(1, row, 0, checked, connect_right)
            if connected:
                if group is not None:
                    self.winning_group = group
                self.winner = 1
                return

        def connect_bottom(row, col):
            return row == self.size - 1

        # check for a player 2 win
        for col in range(self.size):
            # if a cell on the top is connected to the bottom, player 2 wins
            connected, group = self._follow_connection(2, 0, col, checked, connect_bottom)
            if connected:
                if group is not None:
                    self.winning_group = group
                self.winner = 2
                return

        # otherwise, nobody has won
        self.winner = 0
        self.winning_group = None

    def _follow_connection(self, player, start_row, start_col, checked, stop_condition=(lambda r, c: False)):
        # if this isn't the start of a new chain, dont spend time checking
        if self.board[start_row][start_col] != player or checked[start_row][start_col]:
            return False, None

        connected_group = {(start_row, start_col)}

        if stop_condition(start_row, start_col):
            return True, connected_group

        search_queue = [(start_row, start_col)]
        checked[start_row][start_col] = True

        while search_queue:
            y1, x1 = search_queue.pop(0)
            for dy, dx in ADJACENT:
                y2, x2 = (y1 + dy), (x1 + dx)
                # if we find a connected stone, check if we're connected, and add it to the queue
                if self.in_bounds(y2, x2) and self.board[y2][x2] == player and not checked[y2][x2]:
                    connected_group.add((y2, x2))
                    if stop_condition(y2, x2):
                        return True, connected_group

                    search_queue.append((y2, x2))
                    checked[y2][x2] = True
        # if the queue empties, we didn't find the stop condition
        return False, None

    def pretty_print(self):
        # spacing should be odd for things to be consistent
        spacing = 3
        string = '\n' + ' ' * (2 + (spacing + 1) // 2)
        for i in range(self.size):
            string += ('{:' + str(spacing + 1) + '}').format(str(i + 1) + ':')
        string += '\n' + ' ' * (3 + (spacing + 1) // 2) + ('2' + ' ' * spacing) * self.size
        for i, row in enumerate(self.board):
            string += ('\n' + '{:>' + str(2 + i * (spacing + 1) // 2) + '} 1').format(str(i + 1) + ':')
            for j, num in enumerate(row):
                if self.winning_group and (i,j) in self.winning_group and (i,j-1) in self.winning_group:
                    string += ']' + ' ' * (spacing - 2) + '['
                elif self.winning_group and (i,j) in self.winning_group:
                    string += ' ' * (spacing - 1) + '['
                elif self.winning_group and (i,j-1) in self.winning_group:
                    string += ']' + ' ' * (spacing - 1)
                elif self.move_list and self.move_list[-1] == (i,j):
                    string += ' ' * (spacing - 1) + '('
                elif self.move_list and self.move_list[-1] == (i,j-1):
                    string += ')' + ' ' * (spacing - 1)
                else:
                    string += ' ' * spacing

                if num == 0:
                    string += '·'
                else:
                    string += str(num)
            if self.winning_group and (i,self.size-1) in self.winning_group:
                string += ']' + ' ' * (spacing-1)
            elif self.move_list and self.move_list[-1] == (i, self.size-1):
                string += ')' + ' ' * (spacing-1)
            else:
                string += ' ' * spacing
            string += '1'
        string += '\n' + ' ' * (4 + self.size * (spacing + 1) // 2) + (' ' * spacing + '2') * self.size
        print(string)
