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
        self.moveFuncitons = {"P": self.get_pawn_moves, "R" :self.get_rook_moves, "N": self.get_knight_moves,
                              "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []


    """
    Takes a Move as a parameter and executes it (will not work for castling, pawn promotion, and en-passant).
    """


    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)   # log the move so we can undo later
        self.whiteToMove = not self.whiteToMove # swap players
        if move.pieceMoved == "wK":     # update the king's location if moved
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)


    """
    Undo the last move made.
    """


    def undo_move(self):
        if len(self.moveLog) != 0:  # make sure that there is a move to do
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove     # switch turns back
            if move.pieceMoved == "wK":     # update king's position if needed
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

        
    """
    All moves considering checks.
    """


    def get_valid_moves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:   # only one check, block check or move king
                moves = self.get_all_possible_moves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares = []   # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:   # once you get to piece and checks
                            break
                    
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1): # go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != "K":   # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:  # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:   # double check, king has to move
                self.get_king_moves(kingRow, kingCol, moves)
        else:   # not in check so all moves are fine
            moves = self.get_all_possible_moves()
        return moves


    """
    All moves without considering checks
    """

    
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFuncitons[piece](r, c, moves)  # calls appropriate move function baesd on piece type
        return moves


    """
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    """


    def get_pawn_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove:    # white pawn moves
            if self.board[r-1][c] == "--":  # one square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":   # two square pawn advance
                        moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == "b":  # enemy piece to capture
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r-1, c+1), self.board))
        
        else:   # black pawn moves
            if self.board[r+1][c] == "--":   # one square pawn advance
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":   # two square pawn move
                        moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board))

        # add pawn promotions


    """
    Get all the rook moves for the pawn located at row, col and add these moves to the list
    """


    def get_rook_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:       # friendly piece invalids
                            break
                else:       # off board
                    break 


    """
    Get all the knight moves for the pawn located at row, col and add these moves to the list
    """


    def get_knight_moves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0] 
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Get all the bishop moves for the pawn located at row, col and add these moves to the list
    """


    def get_bishop_moves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:       # friendly piece invalids
                            break
                else:       # off board
                    break 


    """
    Get all the queen moves for the pawn located at row, col and add these moves to the list
    """


    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)


    """
    Get all the king moves for the pawn located at row, col and add these moves to the list
    """


    def get_king_moves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:    # not an ally piece 
                    # place king on end square and check for cheks
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.check_for_pins_and_checks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on original location
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)


    """
    Returns if the player is in check, a list of pins, and a list of checks
    """

    def check_for_pins_and_checks(self):
        pins = []   # squares where the allied pinned piece is and direction pinned from
        checks = [] # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()    # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K": # "phantom" king
                        if possiblePin == ():   # first allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:   # second allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) one square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction one square away and piece is a king
                        if (0 <= j <= 3 and type == "R") or \
                           (4 <= j <= 7 and type == "B") or \
                           (i == 1 and type == "P" and ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                           (type == "Q") or \
                           (i == 1 and type == "K"):
                            if possiblePin == ():    # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:   # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:   # enemy piece no applying check
                            break
                else:
                    break   # off board

        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow = m[0]
            endCol = startCol = m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


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