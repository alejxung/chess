"""
Main driver file.
Handling user input.
Displaying current GameStatus object.
"""

import pygame as p
import ChessEngine
import sys

WIDTH = HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}


"""
Initialize a global directory of images.
This will be called exactly once in the main.
"""


def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB' ,'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("chess/images/" + piece + ".png"), (SQUARE_SIZE,SQUARE_SIZE))
        
        
"""
The main driver for our code.
This will handle user input and updating the graphics.
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False # flag variable for when a move is made
    animate = False # flag variable for when we should animate a move
    loadImages() # do this only once before while loop
    running = True
    square_selected = () # no square is selected initially, this will keep track of the last click of the user (tuple(row,col))
    player_clicks = [] # this will keep track of player clicks (two tuples)
    game_over = False

    white_did_check = ""
    black_did_check = ""
    last_move_printed = False
    moves_list = []
    
    turn = 1

    while running:
        for e in p.event.get():  
            if e.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()
            # mouse handler            
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos() # (x, y) location of the mouse
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col): # user clicked the same square twice
                        square_selected = () # deselect
                        player_clicks = [] # clear clicks
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected) # append for both 1st and 2nd click
                    if len(player_clicks) == 2: # after 2nd click                                                                    
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)  
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.makeMove(valid_moves[i])
                                if game_state.checkForPinsAndChecks()[0]:
                                    if not game_state.white_to_move:
                                        white_did_check = "+"
                                    else:
                                        black_did_check = "+"
                                move_made = True
                                animate = True
                                square_selected = () # reset user clicks
                                player_clicks = [] 
                                if game_state.white_to_move:
                                    moves_list.append(f"\n{turn}. {game_state.move_log[-2].getChessNotation()}{white_did_check} {game_state.move_log[-1].getChessNotation()}{black_did_check}")
                                    print(f"\n{turn}. {game_state.move_log[-2].getChessNotation()}{white_did_check} {game_state.move_log[-1].getChessNotation()}{black_did_check}", end= "")
                                    turn += 1
                                    white_did_check = ""
                                    black_did_check = ""
                        if not move_made:
                            player_clicks = [square_selected]
            
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when "z" is pressed
                    if game_state.white_to_move:
                        if turn > 1:
                            turn -= 1
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    last_move_printed = False
                if e.key == p.K_r:  # reset the board when "r" is pressed
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    turn = 1
                    last_move_printed = False
                    moves_list = []
                    
        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
                                          
        drawGameState(screen, game_state, valid_moves, square_selected) 

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawText(screen, "Black wins by checkmate")
                if not last_move_printed:
                    moves_list[-1] += "+"
                    moves_list.append("result: 0-1")
                    print("+")
                    print("result: 0-1")
                    last_move_printed = True
                    saveGame(moves_list)
            else:
                drawText(screen, "White wins by checkmate")
                if not last_move_printed:
                    moves_list.append(f"\n{turn}. {game_state.move_log[-1].getChessNotation()}++")
                    moves_list.append("result: 1-0")
                    print(f"\n{turn}. {game_state.move_log[-1].getChessNotation()}++")
                    print("result: 1-0")
                    last_move_printed = True
                    saveGame(moves_list)

        elif game_state.stalemate:
            game_over = True
            drawText(screen, "Stalemate")
            if not last_move_printed:
                if not game_state.white_to_move():
                    moves_list.append(f"\n{turn}. {game_state.move_log[-1].getChessNotation()}")
                    moves_list.append("result: 1/2-1/2")
                    print(f"\n{turn}. {game_state.move_log[-1].getChessNotation()}")
                    print("result: 1/2-1/2")
                    last_move_printed = True      
                    saveGame(moves_list)

        clock.tick(MAX_FPS)
        p.display.flip()


"""
Highlight square selected and moves for piece selected.
"""


def highlightSquares(screen, game_state, valid_moves, square_selected):
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        surface = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        surface.set_alpha(100)
        surface.fill(p.Color("green"))
        screen.blit(surface, (last_move.end_col*SQUARE_SIZE, last_move.end_row*SQUARE_SIZE))

    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == ("w" if game_state.white_to_move else "b"): # square_selected is a piece that can be moved
            # highlight selected squares
            surface = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            surface.fill(p.Color("blue"))
            screen.blit(surface, (col*SQUARE_SIZE, row*SQUARE_SIZE))
            
            # highlight moves from that square
            surface.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(surface, (SQUARE_SIZE*move.end_col, SQUARE_SIZE*move.end_row))


"""
Responsible for all the graphics within current game state.
"""
    

def drawGameState(screen, game_state, valid_moves, square_selected):
    drawBoard(screen) # draw squares on the board
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board) # draw pieces on top of those squares


"""
Draw the squares on the board.
The top left square is always light.
"""


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row+column) % 2)]
            p.draw.rect(screen, color, p.Rect(column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    

"""
Draw the pieces on the board using the current game_state.board
"""


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


"""
Animating a move.
"""
         
def animateMove(move, screen, board, clock):
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10    # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count+1):
        row, col = (move.start_row + d_row*frame/frame_count, move.start_col + d_col*frame/frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQUARE_SIZE, move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        
        # draw captured piece onto rectangle
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end_square)
        
        # draw moving pieces
        screen.blit(IMAGES[move.piece_moved], p.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)


def saveGame(moves_list):
    result = moves_list.pop()
    turns_dict = {}
    for i in range(len(moves_list)-1,-1,-1):
        try:
            if int(moves_list[i][1]) not in turns_dict:
                turns_dict[moves_list[i][1]] = moves_list[i][1:]+"\n"
        except:
            pass
    file = open("Chess/last_game_logs.txt","w")
    for turn in sorted(turns_dict.keys()):
        file.write(turns_dict[turn])
    file.write(result)
    file.close()


def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, 0, p.Color("grey"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2-text_object.get_width()/2, HEIGHT/2-text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color("black"))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    main()
