import pygame as p
import ChessEngine 

width=height=512
dimension=8
sq_size=width//dimension
max_fps=15
IMAGES={}

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''
def loadImages():
    pieces=['bR','bN','bB','bQ','bK','bB','bN','bR','bp','wR','wN','wB','wQ','wK','wB','wN','wR','wp'] 
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load("images/"+piece+".png"),(sq_size,sq_size))



'''
The main driver for our code. This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen=p.display.set_mode((width,height))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs=ChessEngine.GameState()
    validMoves=gs.getValidMoves()
    moveMade=False
    loadImages()
    sqSelected=()
    playerClicks=[]
    running=True
    while running:
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
            elif e.type==p.MOUSEBUTTONDOWN:
                #print(validMoves)
                location=p.mouse.get_pos()
                col=location[0]//sq_size
                row=location[1]//sq_size
                if sqSelected==(row,col):
                    sqSelected=()
                    playerClicks=[]
                else:
                    sqSelected=(row,col)
                    playerClicks.append((row,col))
                if len(playerClicks)==2:
                    move=ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade=True
                            sqSelected=()
                            playerClicks=[]
                            break
                    if not moveMade:
                        playerClicks=[sqSelected]
                print(gs.whiteToMove)
            elif e.type==p.KEYDOWN:
                if e.key == p.K_ESCAPE:  #exit Escape key pressed
                    running = False
                elif e.key==p.K_z:#undo when z is pressed
                    gs.undoMove()
                    moveMade=True
        if moveMade:
            validMoves=gs.getValidMoves()
            moveMade=False

        drawGameState(screen,gs)
        
        if gs.checkMate:
            gameover=True 
            if gs.whiteToMove:
                drawText(screen,'Black Wins by Checkmate')
            else:
                drawText(screen,'White Wins by Checkmate')
        elif gs.staleMate:
            gameover=True 
            drawText(screen,'Stalemate')


        clock.tick(max_fps)
        p.display.flip()

'''
Responsible for all the graphics within a current game state
'''
def drawGameState(screen,gs):
    drawBoard(screen)
    drawPieces(screen,gs.board)

'''
Draw the squares on the board. The top left square is always light
'''
def drawBoard(screen):
    colors=[(206, 238, 210),(92, 166, 110)]
    for r in range(dimension):
        for c in range(dimension):
            color=colors[(r+c)%2]
            p.draw.rect(screen,color,p.Rect(c*sq_size,r*sq_size,sq_size,sq_size))

'''
Draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen,board):
    for r in range(dimension):
        for c in range(dimension):
            piece=board[r][c]
            if piece!='--':
                screen.blit(IMAGES[piece],p.Rect(c*sq_size,r*sq_size,sq_size,sq_size))

'''
Draws the text on the screen
'''
def drawText(screen,text):
    font=p.font.SysFont("Helvitca",32,True,False)
    textObject=font.render(text,0,p.Color("Gray"))
    textLocation=p.Rect(0,0,width,height).move(width/2 - textObject.get_width()/2,height/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject=font.render(text,0,p.Color('Black'))
    screen.blit(textObject,textLocation.move(2,2))

if __name__=="__main__":
    main()