class white:
    pawn = -1
    knight = -2
    bishop = -3
    rook = -5
    queen = -8
    king = -9

class black:
    pawn = 1
    knight = 2
    bishop = 3
    rook = 5
    queen = 8
    king = 9


class board:
    def __init__(self):
        self.board = [[0] * 8] * 8

        