#holds current state of board
#tells valid moves

class GameState():
    '''
    Initialize the game state.
    - The board is an 8x8 2D list.
    - 'w'/'b' prefix for color, 'p'/'R'/'N'/'B'/'Q'/'K' for type.
    - '--' represents an empty square.
    '''
    def __init__(self):
        self.board=[
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp' for i in range(8)],
            ['--' for i in range(8)],
            ['--' for i in range(8)],
            ['--' for i in range(8)],
            ['--' for i in range(8)],
            ['wp' for i in range(8)],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']
        ]
        self.moveFunctions={'p':self.getPawnMoves,'R':self.getRookMoves,
                            'B':self.getBishopMoves,'N':self.getKnightMoves,
                            'Q':self.getQueenMoves,'K':self.getKingMoves}
        self.whiteToMove=True
        self.moveLog=[]
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False 
        self.staleMate=False
        
        self.enpassantPossible = ()  # coordinates for the square where en passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.wqs,
                                             self.currentCastlingRight.bks, self.currentCastlingRight.bqs)]
        
    
    '''
    Takes a Move parameter and executes it (does not work for castling, pawn promotion, and en-passant)
    '''
    def makeMove(self,move):
        self.board[move.startRow][move.startCol]='--'
        self.board[move.endRow][move.endCol]=move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove= not self.whiteToMove
        #update king's location if moved
        if move.pieceMoved=='wK':
            self.whiteKingLocation=(move.endRow,move.endCol)
        if move.pieceMoved=='bK':
            self.blackKingLocation=(move.endRow,move.endCol)

        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+'Q'
        
        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol]='--'
        #update enpassant possible variable
        if move.pieceMoved[1]=='p' and abs(move.startRow - move.endRow)==2:
            self.enpassantPossible = ((move.startRow+move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible=()

        #castle move
        if move.isCastleMove:
            if move.endCol-move.startCol==2:#kingside castle
                self.board[move.endRow][move.endCol-1]=self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1]='--'
            else:#queenside castle 
                self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2]='--'
        # update castling rights
        self.UpdateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        self.enpassantPossibleLog.append(self.enpassantPossible)

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog)!=0:
            move=self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.pieceMoved
            self.board[move.endRow][move.endCol]=move.pieceCaptured
            self.whiteToMove= not self.whiteToMove
            #update king's location if moved
            if move.pieceMoved=='wK':
                self.whiteKingLocation=(move.startRow,move.startCol)
            if move.pieceMoved=='bK':
                self.blackKingLocation=(move.startRow,move.startCol)

            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # undo castle rights
            self.castleRightsLog.pop()
            self.currentCastlingRight=self.castleRightsLog[-1]
            #undo castle move
            if move.isCastleMove:
                if move.endCol-move.startCol==2:#kingside castle
                    self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1]='--'
                else:#queenside castle 
                    self.board[move.endRow][move.endCol-2]=self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1]='--'

    '''
    Update the castle rights given the move
    '''
    def UpdateCastleRights(self,move):
        if move.pieceMoved=='wK':
            self.currentCastlingRight.wks=False
            self.currentCastlingRight.wqs=False
        elif move.pieceMoved=='bK':
            self.currentCastlingRight.bks=False
            self.currentCastlingRight.bqs=False
        elif move.pieceMoved=='wR':
            if move.startRow==7:
                if move.startCol==0:
                    self.currentCastlingRight.wqs=False
                elif move.startCol==7:
                    self.currentCastlingRight.wks=False
        elif move.pieceMoved=='bR':
            if move.startRow==0:
                if move.startCol==0:
                    self.currentCastlingRight.bqs=False
                elif move.startCol==7:
                    self.currentCastlingRight.bks=False

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)
        moves=self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.whiteToMove=not self.whiteToMove #coz make move already changes this
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove=not self.whiteToMove
            self.undoMove()
        if len(moves)==0:
            if self.inCheck():
                self.checkMate=True 
            else:
                self.staleMate=True 
        else: #needed coz we might do undo
            self.checkMate=False 
            self.staleMate=False
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight=tempCastleRights
        return moves
    
    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
    
    '''
    Determine if the enemy can attack the square r, c
    '''
    def squareUnderAttack(self,r,c):
        self.whiteToMove= not self.whiteToMove 
        oppMoves=self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove 
        for move in oppMoves:
            if move.endRow==r and move.endCol==c:
                return True 
        return False
    
    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves=[]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn,piece=self.board[r][c][0],self.board[r][c][1]
                if (turn=='w' and self.whiteToMove) or (turn=='b' and not self.whiteToMove):
                    self.moveFunctions[piece](r,c,moves)#calls appropriate move function based on piece
        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:
            if self.board[r-1][c]=='--':#1 step forward by white pawn
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=='--':
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1>=0:
                if self.board[r-1][c-1][0]=='b':
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isEnpassantMove=True))
            if c+1<=7:
                if self.board[r-1][c+1][0]=='b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,isEnpassantMove=True))
        else:
            if r+1<=7 and self.board[r+1][c]=='--':#1 step forward by black pawn
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=='--':
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1>=0:
                if self.board[r+1][c-1][0]=='w':
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,isEnpassantMove=True))
            if c+1<=7:
                if self.board[r+1][c+1][0]=='w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isEnpassantMove=True))
            


    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''
    def getRookMoves(self,r,c,moves):
        directions=[(0,1),(0,-1),(1,0),(-1,0)]
        enemy='b' if self.whiteToMove else 'w'
        for dr,dc in directions:
            nr,nc=r,c
            while 0<=nr+dr and nr+dr<8 and 0<=nc+dc and nc+dc<8:
                nr,nc=nr+dr,nc+dc
                if self.board[nr][nc]=='--':
                    moves.append(Move((r,c),(nr,nc),self.board))
                elif self.board[nr][nc][0]==enemy:
                    moves.append(Move((r,c),(nr,nc),self.board))
                    break
                else:
                    break

    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    '''
    def getBishopMoves(self,r,c,moves):
        directions=[(1,1),(1,-1),(-1,1),(-1,-1)]
        enemy='b' if self.whiteToMove else 'w'
        for dr,dc in directions:
            nr,nc=r,c
            while 0<=nr+dr and nr+dr<8 and 0<=nc+dc and nc+dc<8:
                nr,nc=nr+dr,nc+dc
                if self.board[nr][nc]=='--':
                    moves.append(Move((r,c),(nr,nc),self.board))
                elif self.board[nr][nc][0]==enemy:
                    moves.append(Move((r,c),(nr,nc),self.board))
                    break
                else:
                    break

    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list
    '''
    def getKnightMoves(self,r,c,moves):
        directions=[(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
        enemy='b' if self.whiteToMove else 'w'
        for dr,dc in directions:
            if 0<=r+dr<8 and 0<=c+dc<8:
                nr,nc=r+dr,c+dc
                if self.board[nr][nc]=='--':
                    moves.append(Move((r,c),(nr,nc),self.board))
                elif self.board[nr][nc][0]==enemy:
                    moves.append(Move((r,c),(nr,nc),self.board))
                else:
                    pass



    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''
    def getKingMoves(self,r,c,moves):
        directions=[(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        enemy='b' if self.whiteToMove else 'w'
        for dr,dc in directions:
            nr,nc=r,c
            if 0<=nr+dr and nr+dr<8 and 0<=nc+dc and nc+dc<8:
                nr,nc=nr+dr,nc+dc
                if self.board[nr][nc]=='--':
                    moves.append(Move((r,c),(nr,nc),self.board))
                elif self.board[nr][nc][0]==enemy:
                    moves.append(Move((r,c),(nr,nc),self.board))
                else:
                    pass

    '''
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    '''
    def getCastleMoves(self,r,c,moves):
        if self.inCheck():
            return 
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves) 
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r,c,moves)
        
    '''
    Generate kingside castle moves
    '''
    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1]=='--' and self.board[r][c+2]=='--':
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))

    '''
    Generate queenside castle moves
    '''
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))
            

    '''
    Get all the queen moves for the queen located at row, col and add these moves to the list
    '''
    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)
                
class CastleRights():
    '''
    Initialize the castle rights.
    - wks: White King Side
    - bks: Black King Side
    - wqs: White Queen Side
    - bqs: Black Queen Side
    '''
    def __init__(self,wks,bks,wqs,bqs):
        self.wks=wks
        self.bks=bks 
        self.wqs=wqs
        self.bqs=bqs



class Move():

    ranksToRows={'1':7,'2':6,'3':5,'4':4,'5':3,'6':2,'7':1,'8':0}
    rowsToRanks={v:k for k,v in ranksToRows.items()}
    filesToCols={'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
    colsToFiles={v:k for k,v in filesToCols.items()}

    '''
    Initialize the move.
    - startSq: (row, col) of the starting square
    - endSq: (row, col) of the ending square
    - board: the current board state
    - isEnpassantMove: boolean to check if it is an enpassant move
    - isCastleMove: boolean to check if it is a castle move
    '''
    def __init__(self,startSq,endSq,board, isEnpassantMove=False,isCastleMove=False):
        self.startRow=startSq[0]
        self.startCol=startSq[1]
        self.endRow=endSq[0]
        self.endCol=endSq[1]
        self.pieceMoved=board[self.startRow][self.startCol]
        self.pieceCaptured=board[self.endRow][self.endCol]
        self.isPawnPromotion=False 
        if (self.pieceMoved=='wp' and self.endRow==0) or (self.pieceMoved=='bp' and self.endRow==7):
            self.isPawnPromotion=True

        self.isEnpassantMove=isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured='wp' if self.pieceMoved=='bp' else 'bp'
        self.isCastleMove=isCastleMove

        self.moveID=self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol

    '''
    Overriding the equals method
    '''
    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID==other.moveID
        return False

    '''
    Get the chess notation of the move
    '''
    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol)+self.getRankFile(self.endRow,self.endCol)
    
    '''
    Get the rank and file of the square
    '''
    def getRankFile(self,r,c):
        return self.colsToFiles[c]+self.rowsToRanks[r]

