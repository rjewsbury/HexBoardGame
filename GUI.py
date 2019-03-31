from tkinter import *
from board import *
from player import GuiPlayer


class Board:
    # Initialize the board piece images
    def __init__(self, frame, HexBoard):
        self.hexBoard = HexBoard
        self.buttons = [[None]*self.hexBoard.size for i in range(self.hexBoard.size)]
        self.frame = frame
        self.empty_space = PhotoImage(file="blank.png")
        self.red_space = PhotoImage(file="red.png")
        self.blue_space = PhotoImage(file="blue.png")

        self.last_move = None
        self.last_move_player = 0

        # size - to be added in method call when added to ryley's game
        # Square this to get the amount of spaces on the board
        self.SIZE = self.hexBoard.size
        self.IMG_SIZE = 35
        # button size DO NOT CHANGE EVER
        self.SPACE_SIZE = 35
        self.XPADDING = 40
        self.YPADDING = 40
        self.WIN_HEIGHT = 2 * self.YPADDING + self.SIZE * self.IMG_SIZE + 100
        self.WIN_WIDTH = 2 * self.XPADDING + (3 * self.SIZE - 1) * self.IMG_SIZE
        self.draw_board()

    def draw_board(self):
        for row in range(0, self.hexBoard.size):
            j = row * self.SPACE_SIZE + self.XPADDING
            for col in range(0, self.hexBoard.size):
                label = Label(self.frame, image=self.empty_space)
                self.buttons[row][col] = label
                label.pack()
                label.image = self.empty_space
                label.place(anchor=NW, x=j, y=self.YPADDING + row* self.SPACE_SIZE)
                label.bind('<Button-1>', self.on_click_maker(row, col))
                j += 2 * self.SPACE_SIZE

    def coords(self, widget):
        row = (widget.winfo_y() - self.YPADDING) / self.SPACE_SIZE
        col = (widget.winfo_x() - self.XPADDING - row * self.SPACE_SIZE) / (2 * self.SPACE_SIZE)
        return row + 1, col + 1

    def update(self):
        for y in range(self.hexBoard.size):
            for x in range(self.hexBoard.size):
                self.give_colour(y,x,self.hexBoard[y][x])

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

    def on_click_maker(self, y, x):
        def on_click(event):
            # record which button was last clicked
            self.last_move = (y,x)
            # record which player's turn it was when the player clicked
            self.last_move_player = self.hexBoard.turn
        return on_click


class MainWindow:
    def __init__(self, window, HexBoard):
        self.frame = Frame(window)
        self.Board = Board(self.frame, HexBoard)
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


def main(HexBoard, player):
    window = Tk()
    window.wm_title("Hex")
    gameWindow = MainWindow(window, HexBoard)
    for i in (1, -1):
        if isinstance(player[i], GuiPlayer):
            player[i].set_gui(gameWindow)

    def game_loop():
        gameWindow.update()
        player[HexBoard.turn].move(HexBoard)
        gameWindow.update()
        if HexBoard.winner == 0:
            window.after(200, game_loop)
        else:
            # somebody won, show that.
            pass

    window.after(200, game_loop)
    window.mainloop()


if __name__ == "__main__":
    main()
# root.mainloop()  # keep the window up (infinite loop)

# TODO
# undo, resign buttons
# winning screen
# colours for sides
# indicate whose turn it is
# documentation
# ask startup questions via GUI
