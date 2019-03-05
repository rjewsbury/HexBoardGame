from board import HexBoard
from player import TextPlayer, RandomPlayer, AlphaBetaPlayer, ChargeHeuristicPlayer
import time


def text_game():
    size = -1
    while size < 1:
        try:
            # size = int(input('Board size: '))
            size = 11
        except ValueError:
            pass

    swap = False
    while swap not in ('y', 'n'):
        # swap = input('allow swap rule? (y/n): ')
        swap = 'n'
    swap = (swap == 'y')

    player = [None, None, None]
    # auto_types = iter((2, 3))
    for i in (1,-1):
        player_type = -1
        while not (0 <= player_type <= 3):
            try:
                player_type = int(input('0 - Text\n1 - Random (AI)\n2 - Alpha-Beta Search (AI)\n3 - Charge Heuristic (AI)\nplayer %d type?: ' % (i)))
                # player_type = next(auto_types)
            except ValueError:
                pass
        if player_type == 0:
            player[i] = TextPlayer(i)
        elif player_type == 1:
            player[i] = RandomPlayer(i)
        elif player_type == 2:
            use_h = False
            while use_h not in ('y', 'n'):
                # use_h = input('use heuristic sort? (y/n): ')
                use_h = 'y'
            search_depth = 0
            while not search_depth:
                try:
                    search_depth = int(input('search depth?: '))
                    # search_depth = 3
                except ValueError:
                    pass
            player[i] = AlphaBetaPlayer(i, size, search_depth, (use_h == 'y'))
        elif player_type == 3:
            player[i] = ChargeHeuristicPlayer(i, size)

    board = HexBoard(size, swap)

    while board.winner == 0:
        board.pretty_print()
        print('Player', (3-board.turn)//2, 'to move')
        player[board.turn].move(board)

        # if both players are bots, slow down the game
        if not (player[1].is_human() or player[2].is_human()):
            pass # time.sleep(1)

    board.pretty_print()
    print('Player', (3-board.winner)//2, 'Wins!')

def main():
    # text_game()
    import cProfile
    cProfile.run('text_game()', sort='time')


if __name__ == '__main__':
    main()
