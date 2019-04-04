from timeit import default_timer

from board import HexBoard
from heuristic import TwoDistanceHeuristic, ShortestPathHeuristic, ChargeHeuristic
from player import TextPlayer, RandomPlayer, AlphaBetaPlayer, ChargeHeuristicPlayer, GuiPlayer, MonteCarloPlayer
import time
from GUI import main as gui_main

# preset settings for demonstrating the project
DEFAULTS = [
    None,
    {
        'size': 11,
        'swap': 'n',
        'players': [None,
                    AlphaBetaPlayer(1, ShortestPathHeuristic(), 2, sorter=ChargeHeuristic(11)),
                    AlphaBetaPlayer(-1, ShortestPathHeuristic(), 2, sorter=ChargeHeuristic(11))]
    },
    {
        'size': 11,
        'swap': 'n',
        'players': [None,
                    AlphaBetaPlayer(1, TwoDistanceHeuristic(), 2),
                    AlphaBetaPlayer(-1, TwoDistanceHeuristic(), 2)]
    },
    {
        'size':11,
        'swap':'n',
        'players': [None,
                    AlphaBetaPlayer(1, ShortestPathHeuristic(), 2, sorter=ChargeHeuristic(11)),
                    AlphaBetaPlayer(-1, TwoDistanceHeuristic(), 2, sorter=ChargeHeuristic(11))]
    },
    {
        'size': 7,
        'swap': 'n',
        'players': [None,
                    GuiPlayer(1),
                    AlphaBetaPlayer(-1, TwoDistanceHeuristic(), 3, sorter=ChargeHeuristic(7))]
    },
    {
        'size':11,
        'swap':'n',
        'players': [None,
                    GuiPlayer (1),
                    AlphaBetaPlayer(-1, TwoDistanceHeuristic(), 2, sorter=ChargeHeuristic(11))]
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
        while not (0 <= player_type <= 5):
            try:
                player_type = int(input(
                    '0 - Text\n1 - Gui\n2 - Random (AI)\n3 - Alpha-Beta Search (AI)\n'
                    '4 - Monte-Carlo Search (AI)\n5 - Charge Heuristic (AI)\nplayer %d type?: ' % (
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
            player[i] = build_monte_carlo_player(i, size)
        elif player_type == 5:
            player[i] = ChargeHeuristicPlayer(i, size)

    board = HexBoard(size, swap)
    return board, player


# Alpha-Beta is our main AI, and it can be customized to combine different heuristics and time limits
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
    killer_moves = -1
    while killer_moves < 0:
        try:
            killer_moves = int(input('number of killer-moves?: '))
        except ValueError:
            pass
    return AlphaBetaPlayer(player_num, heuristic, search_depth, max_time, sorter, killer_moves)


# Unused monte-carlo player builder - This method is staying for potential future development (if we ever add a monte-
# carlo algorithm)
def build_monte_carlo_player(player_num, size):
    max_time = -1
    while max_time < 0:
        try:
            max_time = int(input('max time per move?: '))
        except ValueError:
            pass
    return MonteCarloPlayer(player_num, size, max_time)


# Text-based UI
def text_game(board, player):
    debug_heuristic = ChargeHeuristic(board.size)
    while board.winner == 0:
        board.pretty_print()
        debug_heuristic.get_child_values(board,True)

        print('Player', board.turn%3, 'to move', '●' if board.turn > 0 else '○')

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
    use_gui = 0
    while use_gui not in ('y', 'n'):
        use_gui = input('use gui? (y/n): ')
    use_gui = (use_gui == 'y')

    preset = -1
    while not (0 <= preset < len(DEFAULTS)):
        try:
            preset = int(input('Preset number 1-%d? (0 for custom):' % (len(DEFAULTS) - 1)))
        except ValueError:
            pass
    main(use_gui, preset)
