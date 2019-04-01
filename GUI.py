from tkinter import *
from board import *
from player import GuiPlayer


class Board:
    # Initialize the board piece images
    def __init__(self, frame, HexBoard):
        self.hexBoard = HexBoard
        self.buttons = [[None]*self.hexBoard.size for i in range(self.hexBoard.size)]
        self.frame = frame
        # Images for the game spaces
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
        # Padding between window edges and buttons
        self.XPADDING = 70
        self.YPADDING = 40
        # Window height/width
        self.WIN_HEIGHT = 2 * self.YPADDING + self.SIZE * self.IMG_SIZE + 100
        self.WIN_WIDTH = 2 * self.XPADDING + (3 * self.SIZE - 1) * self.IMG_SIZE
        self.draw_board()

        # buttons
        resign = Button(self.frame, text="resign", command=self.on_resign_click)
        resign.place(anchor=SW, x=self.XPADDING, y = self.WIN_HEIGHT - self.YPADDING, width=50)
        undo = Button(self.frame, text="undo", command=self.on_undo_click)
        undo.place(anchor=SW, x=self.XPADDING + 70, y = self.WIN_HEIGHT - self.YPADDING, width=50)

        # message label
        self.message_string = StringVar(value="Blue Player's turn to move")
        message = Label(self.frame, textvariable=self.message_string, justify=LEFT, font=("courier new", 15))
        message.place(anchor=SW, x=self.XPADDING + 140, y = self.WIN_HEIGHT - self.YPADDING,
                      width=self.WIN_WIDTH - 2 * self.XPADDING - 140)

        # borders
        # top border
        Label(self.frame, background="#ED3838").place(x=20, y=15, width=self.IMG_SIZE * self.SIZE * 2, height=10)
        # left border
        self.frame.create_line(20, 60, self.IMG_SIZE * self.SIZE+10, self.WIN_HEIGHT-130, fill="#323792",
                               width=10)
        # right border
        self.frame.create_line(self.WIN_WIDTH - self.IMG_SIZE * self.SIZE-50, 30, self.WIN_WIDTH - 60,
                               self.WIN_HEIGHT-160, fill="#323792", width=10)
        # bottom border
        Label(self.frame, background="#ED3838").place(x=40 + self.IMG_SIZE * self.SIZE, y=self.WIN_HEIGHT-120,
                                                      width=self.IMG_SIZE * self.SIZE * 2, height=10)

    def on_resign_click(self):
        self.last_move = "resign"
        self.last_move_player = self.hexBoard.turn

    def on_undo_click(self):
        self.last_move = "undo"
        self.last_move_player = self.hexBoard.turn

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

#    def coords(self, widget):
#        row = (widget.winfo_y() - self.YPADDING) / self.SPACE_SIZE
#        col = (widget.winfo_x() - self.XPADDING - row * self.SPACE_SIZE) / (2 * self.SPACE_SIZE)
#        return row + 1, col + 1

    def update(self):
        for y in range(self.hexBoard.size):
            for x in range(self.hexBoard.size):
                self.give_colour(y,x,self.hexBoard[y][x])

        if self.hexBoard.winner != 0:
            self.message_string.set('%s Player Wins!' % ('Blue' if self.hexBoard.winner == 1 else 'Red'))
        else:
            self.message_string.set("%s Player's turn to move" % ('Blue' if self.hexBoard.turn == 1 else 'Red'))

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
        self.frame = Canvas(window)
        self.Board = Board(self.frame, HexBoard)
        self.frame.config(width=self.Board.WIN_WIDTH, height=self.Board.WIN_HEIGHT)


        self.frame.pack()
        self.hexBoard = HexBoard
    # update the state of board cells, lets viewer know which turn it is
    def update(self):
        self.Board.update()

    # Wait for the player to do something, return that value
    def get_move(self, turn):
        # TODO: set last player to buttons if clicked
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

    window.after(1000, game_loop)
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
