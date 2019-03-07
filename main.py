from board import HexBoard
from heuristic import TwoDistanceHeuristic, ShortestPathHeuristic, ChargeHeuristic
from player import TextPlayer, RandomPlayer, AlphaBetaPlayer, ChargeHeuristicPlayer
import time


def text_game(use_default = False):
    size = -1
    while size < 1:
        try:
            if not use_default:
                size = int(input('Board size: '))
            else:
                size = 11
        except ValueError:
            pass

    swap = False
    while swap not in ('y', 'n'):
        if not use_default:
            swap = input('allow swap rule? (y/n): ')
        else:
            swap = 'n'
    swap = (swap == 'y')

    if not use_default:
        player = [None]*3
    else:
        player = [None,
                  AlphaBetaPlayer(1, ShortestPathHeuristic(), 2, sorter=ChargeHeuristic(size)),
                  AlphaBetaPlayer(-1, ShortestPathHeuristic(), 2, sorter=ChargeHeuristic(size))]
    for i in (1,-1):
        if player[i] is not None:
            continue
        player_type = -1
        while not (0 <= player_type <= 3):
            try:
                player_type = int(input('0 - Text\n1 - Random (AI)\n2 - Alpha-Beta Search (AI)\n3 - Charge Heuristic (AI)\nplayer %d type?: ' % (i%3)))
            except ValueError:
                pass
        if player_type == 0:
            player[i] = TextPlayer(i)
        elif player_type == 1:
            player[i] = RandomPlayer(i)
        elif player_type == 2:
            player[i] = build_alpha_beta_player(i, size)
        elif player_type == 3:
            player[i] = ChargeHeuristicPlayer(i, size)

    board = HexBoard(size, swap)
    while board.winner == 0:
        board.pretty_print()
        print('Player', board.turn%3, 'to move')
        player[board.turn].move(board)

        # if both players are bots, slow down the game
        if not (player[1].is_human() or player[2].is_human()):
            pass # time.sleep(1)

    board.pretty_print()
    print('Player', board.winner%3, 'Wins!')

def build_alpha_beta_player(player_num, size):
    heuristic_type = -1
    heuristic = None
    while not (0 <= heuristic_type <= 1):
        try:
            heuristic_type = int(input('0 - Shortest Path\n1 - Two Distance\nheuristic type?: '))
        except ValueError:
            pass
    if heuristic_type == 0:
        heuristic = ShortestPathHeuristic()
    elif heuristic_type == 1:
        heuristic = TwoDistanceHeuristic()
    use_sort = None
    sorter = None
    while use_sort not in ('y', 'n'):
        use_sort = input('use heuristic sort? (y/n): ')
    if use_sort == 'y':
        sorter = ChargeHeuristic(size)
    search_depth = -2
    while search_depth < -1:
        try:
            search_depth = int(input('search depth? (-1 for iterative): '))
        except ValueError:
            pass
    max_time = 0
    if search_depth < 0:
        while not max_time:
            try:
                max_time = int(input('time per move?: '))
            except ValueError:
                pass
    return AlphaBetaPlayer(player_num, heuristic, search_depth, max_time, sorter)


def main():
    # text_game()
    import cProfile
    cProfile.run('text_game(use_default=True)', sort='time')


if __name__ == '__main__':
    main()
