from timeit import default_timer

from board import HexBoard
from heuristic import TwoDistanceHeuristic, ShortestPathHeuristic, ChargeHeuristic
from player import TextPlayer, RandomPlayer, AlphaBetaPlayer, ChargeHeuristicPlayer, GuiPlayer
import time
from GUI import main as gui_main

DEFAULTS = [
    None,
    {
        'size':11,
        'swap':'n',
        'players':[None,
                  AlphaBetaPlayer(1, TwoDistanceHeuristic(), max_time=20, sorter=ChargeHeuristic(11)),
                  AlphaBetaPlayer(-1, TwoDistanceHeuristic(), max_time=20, sorter=ChargeHeuristic(11))]
    },
    {
        'size':6,
        'swap':'n',
        'players':[None,
                  AlphaBetaPlayer(1, TwoDistanceHeuristic(), 3, sorter=ChargeHeuristic(11)),
                  GuiPlayer(-1)]
    },
]


def text_get_rules(default=0):
    size = -1
    while size < 1:
        try:
            if not default:
                size = int(input('Board size: '))
            else:
                size = DEFAULTS[default]['size']
        except ValueError:
            pass

    swap = False
    while swap not in ('y', 'n'):
        if not default:
            swap = input('allow swap rule? (y/n): ')
        else:
            swap = DEFAULTS[default]['swap']
    swap = (swap == 'y')

    if not default:
        player = [None] * 3
    else:
        player = DEFAULTS[default]['players']
    for i in (1, -1):
        if player[i] is not None:
            continue
        player_type = -1
        while not (0 <= player_type <= 3):
            try:
                player_type = int(input(
                    '0 - Text\n1 - Gui\n2 - Random (AI)\n3 - Alpha-Beta Search (AI)\n'
                    '4 - Charge Heuristic (AI)\nplayer %d type?: ' % (
                                i % 3)))
            except ValueError:
                pass
        if player_type == 0:
            player[i] = TextPlayer(i)
        elif player_type == 1:
            player[i] = GuiPlayer(i)
        elif player_type == 2:
            player[i] = RandomPlayer(i)
        elif player_type == 3:
            player[i] = build_alpha_beta_player(i, size)
        elif player_type == 4:
            player[i] = ChargeHeuristicPlayer(i, size)

    board = HexBoard(size, swap)
    return board, player


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


def text_game(board, player):
    debug_heuristic = TwoDistanceHeuristic()
    while board.winner == 0:
        board.pretty_print()
        # debug_heuristic.get_value(board,True)

        print('Player', board.turn%3, 'to move')

        start = default_timer()
        player[board.turn].move(board)

        print('took %.2f seconds' % (default_timer()-start))

        # if both players are bots, slow down the game
        # if not (player[1].is_human() or player[2].is_human()):
        #     time.sleep(1)

    board.pretty_print()
    print('Player', board.winner%3, 'Wins!')


def main(use_gui=True, default=0):
    board, player = text_get_rules(default)

    # if one of the players is a GUI player, we're forced to use the gui
    has_gui_player = False
    for p in player:
        if isinstance(p, GuiPlayer):
            has_gui_player = True

    if has_gui_player or use_gui:
        gui_main(board, player)
    else:
        text_game(board, player)
#    import cProfile
#    cProfile.run('text_game(use_default=True)', sort='time')


if __name__ == '__main__':
    main(False, 2)
