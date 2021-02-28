"""
This is our main driver file. It will be responsible for 
handling over input and displaying the current GameState object.
"""


import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512  # another option is 400
DIMENSION = 8  # dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations
IMAGES = {}



"""
Initialize a global dictionary of images. 
This will be called exactly once in the main.
"""


def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ", ]
    for piece in pieces:
        # NOTE: we can access an image by saying IMAGES["wp"]
        # images are scaled by SQ_SIZE
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


"""
The main driver for our code. 
This will handle user input and updating the graphics.
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()  # calling constructor
    load_images()  # only do this once, before while loop
    running = True
    sqSelected = () # no square is selecetd, keep track of the last click of the user - tuple: (row, col)
    playerClicks = []   # keep track of player clicks - two tuples: [(6, 4), (4, 4)]
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()    # (x, y) location of mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):    # user clicked the same square => undo
                    sqSelected = ()             # deselect
                    playerClicks = []           # clear player clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) # append for both first and second clikcs
                if len(playerClicks) == 2:      # after second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.get_chess_notation())
                    gs.make_move(move)
                    sqSelected = ()     # reset user clicks
                    playerClicks = []
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when "z" is pressed
                    gs.undo_move()


        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Responsible for all the graphics within a current game state.
"""


def draw_game_state(screen, gs):
    draw_board(screen)  # draw squares on the board
    # add in piece highlighting or move suggestions
    draw_pieces(screen, gs.board)  # draw pieces on top of those squares


"""
Draw the squares on the board. The top left square is always light.
"""


def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draw the pieces on the board using the current GameState.board
"""


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()