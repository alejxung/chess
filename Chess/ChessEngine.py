"""
This class is responsible for storing all the 
information about the current state of a class game. 
It will also be responsible for determining the valid moves 
at the current state. It will also keep a move log.
"""


class GameState():
    def __init__(self):
        # board is an 8x8 2D list, each element of the list has 2 characters,
        # the first char represents the color of the piece, "b" or "w"
        # the second char represents the type of the piece, "K", "Q", "R", "B", "N", "P"
        # "--" represents an empty space with no piece --> easier to parse
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"], # view of white piece
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"], 
            ["--", "--", "--", "--", "--", "--", "--", "--"], 
            ["--", "--", "--", "--", "--", "--", "--", "--"], 
            ["--", "--", "--", "--", "--", "--", "--", "--"], 
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []


    """
    Takes a Move as a parameter and executes it (will not work for castling, pawn promotion, and en-passant).
    """


    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)   # log the move so we can undo later
        self.whiteToMove = not self.whiteToMove # swap players


    """
    Undo the last move made.
    """


    def undo_move(self):
        if len(self.moveLog) != 0:  # make sure that there is a move to do
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove     # switch turns back

    
    """
    All moves considering checks.
    """

    def get_valid_moves(self):
        return self.get_all_possible_moves()  


    """
    All moves without considering checks
    """

    
    def get_all_possible_moves(self):
        moves = [Move((6, 4), (4, 4), self.board)]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) and (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == "P":
                        self.get_pawn_moves(r, c, moves)
                    elif piece == "R":
                        self.get_rook_moves(r, c, moves)
        return moves


        """
        Get all the pawn moves for the pawn located at row, col and add these moves to the list
        """


        def get_pawn_moves(self, r, c, moves):
            pass


        """
        Get all the rook moves for the pawn located at row, col and add these moves to the list
        """


        def get_rook_moves(self, r, c, moves):
            pass


class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, 
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, 
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        print(self.moveID)

    
    """
    Overriding the equals method.
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        # can add to make this like real chess notation
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]