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