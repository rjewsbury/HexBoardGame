from tkinter import *
from math import *
from time import sleep

# size - to be added in method call when added to ryley's game
# Square this to get the amount of spaces on the board
SIZE = 9
# Find out what these do through trial/error. I currently have no clue. Window/board height/width?
X = 40
Y = 40
IMG_SIZE = 35
# button size DO NOT CHANGE EVER
SPACE_SIZE = 35
XPADDING = 40
YPADDING  = 40
WIN_HEIGHT = 2 * YPADDING + SIZE * IMG_SIZE + 100
WIN_WIDTH = 2 * XPADDING + (3 * SIZE - 1) * IMG_SIZE


class Board:
    player = 0
    # Initialize the board piece images
    def __init__(self, frame):
        self.frame = frame
        self.empty_space = PhotoImage(file="blank.png")
        self.red_space = PhotoImage(file="red.png")
        self.blue_space = PhotoImage(file="blue.png")
        self.draw_board()

    def draw_board(self):
        for i in range(0, SIZE):
            j = i * SPACE_SIZE + X
            for a in range(0, SIZE):
                label = Label(self.frame, image=self.empty_space)
                label.pack()
                label.image = self.empty_space
                label.place(anchor=NW, x=j, y=YPADDING + i * SPACE_SIZE)
                label.bind('<Button-1>', self.on_click)
                j += 2 * SPACE_SIZE

    def coords(self, widget):
        row = (widget.winfo_y() - Y) / SPACE_SIZE
        col = (widget.winfo_x() - X - row * SPACE_SIZE) / (2 * SPACE_SIZE)
        return row + 1, col + 1

    def on_click(self, event):
        if event.widge.image != self.empty_space:
            return
        self.give_colour(event.widget)


    def give_colour(self, widget):
        if self.player == 0:
            widget.config(image=self.red_space)
            widget.image = self.red_space
        else:
            widget.config(image=self.blue_space)
            widget.image = self.blue_space

    def on_click(self, event):
        # Make sure nothing happens if the space already has a colour
        if event.widget.image != self.empty_space:
            return
        self.give_colour(event.widget)
        self.player = (self.player + 1) % 2


class mainWindow:
    def __init__(self, window):
        self.frame = Frame(window, width=WIN_WIDTH, height=WIN_HEIGHT)
        self.Board = Board(self.frame)
        self.frame.pack()


def main():
    window = Tk()
    window.wm_title("Hex")
    mainWindow(window)
    window.mainloop()


main()
# root.mainloop()  # keep the window up (infinite loop)

# 1: make canvas
# 2. put canvas in frame
# 3. put a polygon of some kind in the canvas
# 4. Somehow duplicate the polygons
# 5. Add buttons (undo, resign, etc)
