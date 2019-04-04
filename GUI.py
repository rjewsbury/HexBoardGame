"""
GUI.py
Written by Caleigh
Modified by Caleigh and Ryley
This file handles all visuals and user input
"""

from tkinter import *
from player import GuiPlayer


# Board class
# Deals with drawing the game board and all its spaces and their colours, to be placed inside the window class
class Board:
    # Initialize the board piece images
    def __init__(self, frame, hex_board):
        self.hexBoard = hex_board
        self.buttons = [[None]*self.hexBoard.size for i in range(self.hexBoard.size)]
        self.frame = frame
        # Images for the game spaces
        self.empty_space = PhotoImage(file="blank.png")
        self.red_space = PhotoImage(file="red.png")
        self.blue_space = PhotoImage(file="blue.png")
        # Initialize the remembered moves
        self.last_move = None
        self.last_move_player = 0
        # Square this to get the amount of spaces on the board
        self.SIZE = self.hexBoard.size
        self.IMG_SIZE = 35
        # button size DO NOT CHANGE EVER!!!
        self.SPACE_SIZE = 35
        # Padding between window edges and buttons
        self.XPADDING = 70
        self.YPADDING = 40
        # Window height/width
        self.WIN_HEIGHT = 2 * self.YPADDING + self.SIZE * self.IMG_SIZE + 100
        self.WIN_WIDTH = 2 * self.XPADDING + (3 * self.SIZE - 1) * self.IMG_SIZE

        self.draw_board()

        # Resign and undo buttons
        resign = Button(self.frame, text="resign", command=self.on_resign_click)
        resign.place(anchor=SW, x=self.XPADDING, y=self.WIN_HEIGHT - self.YPADDING, width=50)
        undo = Button(self.frame, text="undo", command=self.on_undo_click)
        undo.place(anchor=SW, x=self.XPADDING + 70, y=self.WIN_HEIGHT - self.YPADDING, width=50)

        # message label - declares the current turn or the winner of the game
        self.message_string = StringVar(value="Blue Player's turn to move")
        message = Label(self.frame, textvariable=self.message_string, justify=LEFT, font=("courier new", 15))
        message.place(anchor=SW, x=self.XPADDING + 140, y=self.WIN_HEIGHT - self.YPADDING,
                      width=self.WIN_WIDTH - 2 * self.XPADDING - 140)

        # borders:
        # top border
        self.frame.create_line(30, 20, self.IMG_SIZE * self.SIZE * 2 + 20, 20, fill="#ED3838", width=10)
        # left border
        self.frame.create_line(20, 60, self.IMG_SIZE * self.SIZE + 10, self.WIN_HEIGHT-130, fill="#323792",
                               width=10)
        # right border
        self.frame.create_line(self.WIN_WIDTH - self.IMG_SIZE * self.SIZE-50, 30, self.WIN_WIDTH - 60,
                               self.WIN_HEIGHT-160, fill="#323792", width=10)
        # bottom border
        self.frame.create_line(40 + self.IMG_SIZE * self.SIZE, self.WIN_HEIGHT - 115,
                               self.WIN_WIDTH - self.XPADDING, self.WIN_HEIGHT - 115, fill="#ED3838", width=10)

    # The below methods deal with button handling for undo and resign
    # resign
    def on_resign_click(self):
        self.last_move = "resign"
        self.last_move_player = self.hexBoard.turn

    # undo
    def on_undo_click(self):
        self.last_move = "undo"
        self.last_move_player = self.hexBoard.turn

    # Now put everything together!
    def draw_board(self):
        for row in range(0, self.hexBoard.size):
            j = row * self.SPACE_SIZE + self.XPADDING
            for col in range(0, self.hexBoard.size):
                label = Label(self.frame, image=self.empty_space)
                self.buttons[row][col] = label
                label.pack()
                label.image = self.empty_space
                label.place(anchor=NW, x=j, y=self.YPADDING + row * self.SPACE_SIZE)
                label.bind('<Button-1>', self.on_click_maker(row, col))
                j += 2 * self.SPACE_SIZE

    # Board gets players next move and updates itself with the correct space colours
    def update(self):
        for y in range(self.hexBoard.size):
            for x in range(self.hexBoard.size):
                self.give_colour(y, x, self.hexBoard[y][x])

        if self.hexBoard.winner != 0:
            self.message_string.set('%s Player Wins!' % ('Blue' if self.hexBoard.winner == 1 else 'Red'))
        else:
            self.message_string.set("%s Player's turn to move" % ('Blue' if self.hexBoard.turn == 1 else 'Red'))

    # Change the colour of a board piece
    def give_colour(self, y, x, player):
        widget = self.buttons[y][x]
        if player == -1:
            widget.config(image=self.red_space)
            widget.image = self.red_space
        elif player == 1:
            widget.config(image=self.blue_space)
            widget.image = self.blue_space
        else:
            widget.config(image=self.empty_space)
            widget.image = self.empty_space

    # on_click_maker allows us to pass parameters to a button's on-click event so that we can modify variables
    # outside scope
    def on_click_maker(self, y, x):
        def on_click(event):
            # record which button was last clicked
            self.last_move = (y, x)
            # record which player's turn it was when the player clicked
            self.last_move_player = self.hexBoard.turn
        return on_click


# The window containing the game board, continuously stays open
class MainWindow:
    def __init__(self, window, hex_board):
        self.frame = Canvas(window)
        self.Board = Board(self.frame, hex_board)
        self.frame.config(width=self.Board.WIN_WIDTH, height=self.Board.WIN_HEIGHT)
        self.frame.pack()

    # update the state of board cells, lets viewer know which turn it is
    def update(self):
        self.Board.update()

    # Wait for the player to do something, return that value
    def get_move(self, turn):
        if turn == self.Board.last_move_player:
            return self.Board.last_move
        else:
            return None

    def reset_move(self):
        self.Board.last_move = None
        self.Board.last_move_player = 0


# GUI main
def main(hex_board, player):
    window = Tk()
    window.wm_title("Hex")
    game_window = MainWindow(window, hex_board)
    for i in (1, -1):
        if isinstance(player[i], GuiPlayer):
            player[i].set_gui(game_window)

    # Keep the main window updating
    def game_loop():
        game_window.update()
        player[hex_board.turn].move(hex_board)
        game_window.update()
        if hex_board.winner == 0:
            window.after(200, game_loop)
        else:
            # somebody won, show that.
            pass

    window.after(1000, game_loop)
    window.mainloop()
