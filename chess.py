from chess_logic_by_thomasahle import *
# from minimax import *
# from chess import *

answer = raw_input("Would you like to evolve the heuristic? (y/n)")
if answer == 'y':
    state = Position(initial, 0, (True,True), (True,True), 0, 0)
    # print state
    heuristic = evolve(state, 5, 3, tournament, maxgen=50)
    heuristic.display()
# pos = Position(initial, 0, (True,True), (True,True), 0, 0)
# main()


