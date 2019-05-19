from __future__ import print_function
import re, sys, time
import random
# from chess import *
from chess_logic_by_thomasahle import *
# from chess_logic_by_thomasahle import HEURISTIC
from genetic_programming import*
from itertools import count
from collections import OrderedDict, namedtuple



###############################################################################
# Search logic
###############################################################################

# lower <= s(pos) <= upper
# Entry = namedtuple('Entry', 'lower upper')

# The normal OrderedDict doesn't update the position of a key in the list,
# when the value is changed.
# class LRUCache:
#     '''Store items in the order the keys were last added'''
#     def __init__(self, size):
#         self.od = OrderedDict()
#         self.size = size

#     def get(self, key, default=None):
#         try: self.od.move_to_end(key)
#         except KeyError: return default
#         return self.od[key]

#     def __setitem__(self, key, value):
#         try: del self.od[key]
#         except KeyError:
#             if len(self.od) == self.size:
#                 self.od.popitem(last=False)
#         self.od[key] = value

#######################################################################################
# Minimax with Alpha Beta Pruning - adapted from UC Berkeley CS188 multiagent project
#######################################################################################
class Minimax:
    def __init__(self, heuristic):
        # self.tp_score = LRUCache(TABLE_SIZE)
        # self.tp_move = LRUCache(TABLE_SIZE)
        # self.nodes = 0
        self.heuristic = heuristic

    # def bound(self, pos, gamma, depth, root=True):
    #     """ returns r where
    #             s(pos) <= r < gamma    if gamma > s(pos)
    #             gamma <= r <= s(pos)   if gamma <= s(pos)"""
    #     self.nodes += 1

    #     # Depth <= 0 is QSearch. Here any position is searched as deeply as is needed for calmness, and so there is no reason to keep different depths in the transposition table.
    #     depth = max(depth, 0)

    #     # Sunfish is a king-capture engine, so we should always check if we
    #     # still have a king. Notice since this is the only termination check,
    #     # the remaining code has to be comfortable with being mated, stalemated
    #     # or able to capture the opponent king.
    #     if pos.score <= -MATE_LOWER:
    #         return -MATE_UPPER

    #     # Look in the table if we have already searched this position before.
    #     # We also need to be sure, that the stored search was over the same
    #     # nodes as the current search.
    #     entry = self.tp_score.get((pos, depth, root), Entry(-MATE_UPPER, MATE_UPPER))
    #     if entry.lower >= gamma and (not root or self.tp_move.get(pos) is not None):
    #         return entry.lower
    #     if entry.upper < gamma:
    #         return entry.upper

    #     # Here extensions may be added
    #     # Such as 'if in_check: depth += 1'

    #     # Generator of moves to search in order.
    #     # This allows us to define the moves, but only calculate them if needed.
    #     def moves():
    #         # First try not moving at all
    #         if depth > 0 and not root and any(c in pos.board for c in 'RBNQ'):
    #             yield None, -self.bound(pos.nullmove(), 1-gamma, depth-3, root=False)
    #         # For QSearch we have a different kind of null-move
    #         if depth == 0:
    #             yield None, pos.score
    #         # Then killer move. We search it twice, but the tp will fix things for us. Note, we don't have to check for legality, since we've already done it before. Also note that in QS the killer must be a capture, otherwise we will be non deterministic.
    #         killer = self.tp_move.get(pos)
    #         if killer and (depth > 0 or pos.value(killer) >= QS_LIMIT):
    #             yield killer, -self.bound(pos.move(killer), 1-gamma, depth-1, root=False)
    #         # Then all the other moves
    #         for move in sorted(pos.gen_moves(), key=pos.value, reverse=True):
    #             if depth > 0 or pos.value(move) >= QS_LIMIT:
    #                 yield move, -self.bound(pos.move(move), 1-gamma, depth-1, root=False)

    #     # Run through the moves, shortcutting when possible
    #     best = -MATE_UPPER
    #     for move, score in moves():
    #         best = max(best, score)
    #         if best >= gamma:
    #             # Save the move for pv construction and killer heuristic
    #             self.tp_move[pos] = move
    #             break

    #     # Stalemate checking is a bit tricky: Say we failed low, because
    #     # we can't (legally) move and so the (real) score is -infty.
    #     # At the next depth we are allowed to just return r, -infty <= r < gamma,
    #     # which is normally fine.
    #     # However, what if gamma = -10 and we don't have any legal moves?
    #     # Then the score is actaully a draw and we should fail high!
    #     # Thus, if best < gamma and best < 0 we need to double check what we are doing.
    #     # This doesn't prevent sunfish from making a move that results in stalemate,
    #     # but only if depth == 1, so that's probably fair enough.
    #     # (Btw, at depth 1 we can also mate without realizing.)
    #     if best < gamma and best < 0 and depth > 0:
    #         is_dead = lambda pos: any(pos.value(m) >= MATE_LOWER for m in pos.gen_moves())
    #         if all(is_dead(pos.move(m)) for m in pos.gen_moves()):
    #             in_check = is_dead(pos.nullmove())
    #             best = -MATE_UPPER if in_check else 0

    #     # Table part 2
    #     if best >= gamma:
    #         self.tp_score[(pos, depth, root)] = Entry(best, entry.upper)
    #     if best < gamma:
    #         self.tp_score[(pos, depth, root)] = Entry(entry.lower, best)

    #     return best

    # # secs over maxn is a breaking change. Can we do this?
    # # I guess I could send a pull request to deep pink
    # # Why include secs at all?
    # def _search(self, pos):
    #     """ Iterative deepening MTD-bi search """
    #     self.nodes = 0

    #     # In finished games, we could potentially go far enough to cause a recursion
    #     # limit exception. Hence we bound the ply.
    #     for depth in range(1, 1000):
    #         self.depth = depth
    #         # The inner loop is a binary search on the score of the position.
    #         # Inv: lower <= score <= upper
    #         # 'while lower != upper' would work, but play tests show a margin of 20 plays better.
    #         lower, upper = -MATE_UPPER, MATE_UPPER
    #         while lower < upper - EVAL_ROUGHNESS:
    #             gamma = (lower+upper+1)//2
    #             score = self.bound(pos, gamma, depth)
    #             if score >= gamma:
    #                 lower = score
    #             if score < gamma:
    #                 upper = score
    #         # We want to make sure the move to play hasn't been kicked out of the table,
    #         # So we make another call that must always fail high and thus produce a move.
    #         score = self.bound(pos, lower, depth)

    #         # Yield so the user may inspect the search
    #         yield

    # evaluation_function = None
    # heuristic = None
    
    def heuristic_func(self, pc, state):
        # to be changed; should not make new tree each move
        # maybe move to main() or Position class
        evaluation = makerandomtree(pc, state)
        return evaluation
        

    def evaluate(self, state, index):
        # to be changed; should not make new tree each move
        # evaluation_function.display()
        # if not self.heuristic:
        # self.heuristic.display()
        # return state.evaluation()
        # print(state)
        # return random.randint(0, 1000)
        # print(state.evaluation())
        # return state.evaluation()
        # self.heuristic.display()
        # print(self.heuristic.evaluate(state))
        return self.heuristic.evaluate(state)

    # def evaluate(self, state, index):
        # Essentially a random number geneator 
    #     evaluation_function = self.heuristic_func(2, state)
    #     print(evaluation_function.evaluate(state))
    #     return evaluation_function.evaluate(state)


    def solution(self, state):
        actions = []
        depth = 3
        alpha = -999999999
        beta = 999999999
        score = self.value(0, state, depth , alpha, beta)
        for move in state.gen_moves():
            actions.append(move)

        solutions = {action : self.value(0, state.move(action), depth, alpha, beta) for action in actions}
        return max(solutions, key = solutions.get), score

    def value(self, index, state, depth, alpha, beta):
        index += 1
        getNumAgents = 2
        if index >= getNumAgents:
            index = 0
            depth -= 1
        # if state.isWin() or state.isLose() or depth <= 0:
        #     return self.evaluationFunction(state)
        if depth <= 0:
            return self.evaluate(state, index)
        elif index == 0:
            return self.max_value(index, state, depth, alpha, beta)
        else:
            return self.min_value(index, state, depth, alpha, beta)


    def max_value(self, index, game_state, depth, alpha, beta):
        score = -999999999
        actions = []
        for move in game_state.gen_moves():
            actions.append(move)
        successors = [game_state.move(action) for action in actions]
        # for state in successors:
        #     score = max(score, self.value(index, state, depth))

        for action in actions:
            state = game_state.move(action)
            score = max(score, self.value(index+1, state, depth, alpha, beta))
            beta = min(beta, score)
            if score > beta:
                return score
            alpha = max(alpha, score)
        return score

    def min_value(self, index, game_state, depth, alpha, beta):
        score = 999999999
        actions = []
        for move in game_state.gen_moves():
            actions.append(move)
        successors = [game_state.move(action) for action in actions]
        # for state in successors:
        #     score = min(score, self.value(index, state, depth))
        for action in actions:
                state = game_state.move(action)
                score = min(score, self.value(index+1, state, depth, alpha, beta))
                # print score
                # print alpha
                alpha = max(alpha, score)
                if score < alpha:
                    return score
                beta = min(beta, score)
        return score

    def search(self, pos, secs):
        move = self.solution(pos)
        return move
        