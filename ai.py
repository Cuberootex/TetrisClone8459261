from random import randint

from time import sleep as wait
import blocks
import config as cnf
import copy

class AI:
    """
    'AI' class, takes a grid, evaluates the best move for the current Tetromino
    and computes a very basic move sequence which allows the Tetromino
    to be moved in the best position..
    """

    # 2023 notes: "AI" here is too strong of a word. This is really a fancy algorithm.
    # Nothing more.

    def __init__(self, grid, field, minWait, maxWait, slow):
        self.grid = grid
        self.field = field
        self.minWait = minWait
        self.maxWait = maxWait
        self.slow = slow

        self.debugPiece = None
        self.debugGhostPos = []
        self.debugGhostIdx = 0
        self.debugWait = 0
        self.moveQueue = []  # FIFO
        self.moveWait = 0

    def generateHardDropPos(self, piece):
        """
        Generate all possible positions obtained from hard-dropping
        a given piece, including every rotation possible.
        """
        pieceCopy = copy.deepcopy(piece)
        pieceBBSize = pieceCopy.getBBSize()[0]
        gridContents = [x[:] for x in self.grid.contentsLocked]
        linesWithMinos = 0

        for x in range(cnf.gameGridY + self.grid.getExtraHeight() - 1, 0, -1):
            if gridContents[x] != [0] * cnf.gameGridX:
                linesWithMinos += 1
            else:
                break

        curX = 0 - pieceBBSize // 2
        curY = cnf.gameGridY + self.grid.getExtraHeight() - linesWithMinos - pieceBBSize
        validPositions = []

        maxRotations = 4

        if piece == blocks.I_mino or piece == blocks.S_mino or piece == blocks.Z_mino:
            maxRotations = 2
        elif piece == blocks.O_mino:
            maxRotations = 1


        for rotation in range(maxRotations):
            for x in range(curX, cnf.gameGridX - 1):
                pieceCopy.setPosition((x, curY))
                if self.grid.chkPieceOOB(pieceCopy) == 0:
                    while self.grid.moveMino(pieceCopy, 2, True):
                        pieceCopy = self.grid.moveMino(pieceCopy, 2)[0]
                    validPositions.append((x, pieceCopy.getPosition()[1], rotation))
            pieceCopy.rotate(0)
        return validPositions

    def evaluateGrid(self, gridToEvaluate, pieceId=99, linesCleared=0):
        """
        Assign a score to a game grid, based on various parameters.
        The importance of each paramter can be adjusted with the constants listed below.
        This is where a ton of work is needed because the current parameters and constants are quite garbage...

        TODO: I-dependency definition is wrong and broken...
        """


        # Constants :
        tetrisWeight = cnf.tetrisWeight

        c0 = 100  # Lines cleared
        lineClearFact1 = 50
        c1 = -600  # Max altitude
        c2 = -3500  # Holes
        c3 = -15  # Roughness
        c4 = -32  # Difference in height between tallest and smallest column
        c5 = -30  # Aggregate height
        c6 = -50  # Consecutive holes in columns
        c7 = 0 # Penalty if current piece blocks well
        c8 = 0 # Penalty for moves in the center
        c9 = -1000 # minos above holes
        c10 = -800  # I-dependency penalty
        c11 = 240  # highest empty cell column (piece burning related stuff), coef updated below

        wellDepth = 2
        lineClears = linesCleared
        maxAltitude = 40
        holes = 0
        roughness = 0
        columnDiff = 0
        aggregHeight = 0
        blocksWell = 0
        center = 0
        IDependencies = 0

        minosInColumns = [0] * cnf.gameGridX
        minoMaxHeightCol = [0] * cnf.gameGridX
        holesInColumns = [0] * cnf.gameGridX
        minosAboveHoles = 0
        totalHolesInColumns = 0

        emptyCellCntTotal = [0] * cnf.gameGridX


        for lineIdx in range(len(gridToEvaluate) - 1, 1, -1):
            curLine = gridToEvaluate[lineIdx]
            lineAbove = gridToEvaluate[lineIdx - 1]
            if curLine == [0] * cnf.gameGridX and lineAbove == [0] * cnf.gameGridX:
                maxAltitude = (cnf.gameGridY + self.grid.getExtraHeight()) - lineIdx - 1
                break
            
            # Check holes and roughness:
            emptyCellCount = 0
            emptyCellIdx = 0
            for idx, mino in enumerate(curLine):
                if mino == 0:
                    emptyCellCount += 1
                    emptyCellIdx = idx

                if mino != 0:
                    minosInColumns[idx] += 1
                    if lineIdx < len(gridToEvaluate) - 1:
                        if gridToEvaluate[lineIdx + 1][idx] == 0:
                            holes += 1
                if mino == pieceId:
                    if cnf.gameGridX // 2 - 2 <= idx <= cnf.gameGridX // 2 + 2:
                        center += 1
                    try:
                        minoBelow = gridToEvaluate[lineIdx + 1][idx]
                        minoBelow1 = gridToEvaluate[lineIdx + 2][idx]
                        if minoBelow == minoBelow1 == 0:
                            blocksWell += 2
                    except:
                        pass
            if emptyCellCount == 1:
                emptyCellCntTotal[emptyCellIdx] += 1

        highestEmptyCellCnt = max(emptyCellCntTotal)

        if highestEmptyCellCnt == 1:
            c11 *= 2
        elif highestEmptyCellCnt == 2 and holes == 0 and self.field.speedLevel < 16:
            c11 *= 3
        elif highestEmptyCellCnt == 3 and holes == 0 and IDependencies == 0:
            c11 *= 4
        elif highestEmptyCellCnt == 4 and holes == 0 and IDependencies == 0 and maxAltitude < 6 + int(tetrisWeight * 4):
            c11 *= int(tetrisWeight * 99)


        # Get holes in columns:
        for x in range(cnf.gameGridX):
            try:
                col = [r[x] for r in gridToEvaluate][len(gridToEvaluate) - maxAltitude:len(gridToEvaluate)]
                minoFound = False
                altitude = len(gridToEvaluate) - (len(gridToEvaluate) - maxAltitude)
                numMinos = 0
                for mino in col:
                    if mino != 0 and mino != 8:
                        if minoMaxHeightCol[x] == 0:
                            minoMaxHeightCol[x] = altitude
                        numMinos += 1
                        minoFound = True
                    elif mino == 0 and minoFound:
                        holesInColumns[x] += 1
                        minosAboveHoles += numMinos
                        numMinos = 0
                    altitude -= 1
            except:
                pass


        # Calculate roughness: obtained by summing the absolute difference in height between two columns
        for i in range(len(minosInColumns) - 1):
            roughness += abs(minosInColumns[i] - minosInColumns[i + 1]) * (2/3 * abs(abs((cnf.gameGridX)//2-i)-(cnf.gameGridX//2)))

        for x in holesInColumns:
            totalHolesInColumns += x

        # Calculate height difference between the tallest columns and the aggregate height,
        # aka the sum of the height of each column.
        # Additionally, detect any I-dependencies.

        '''for i, col in enumerate(minoMaxHeightCol):
            if i == 0:
                nextCol = minoMaxHeightCol[i+1]
                if nextCol - col >= wellDepth:
                    IDependencies += (nextCol - col) // wellDepth
            elif i == cnf.gameGridX - 1:
                prevCol = minoMaxHeightCol[i - 1]
                if prevCol - col >= wellDepth:
                    IDependencies += (prevCol - col) // wellDepth
            else:
                prevCol = minoMaxHeightCol[i-1]
                nextCol = minoMaxHeightCol[i+1]
                if prevCol - col >= wellDepth and nextCol - col >= wellDepth:
                    IDependencies += 1'''

        if abs(minoMaxHeightCol[0] - minoMaxHeightCol[1]) >= wellDepth:
            IDependencies += abs(minoMaxHeightCol[0] - minoMaxHeightCol[1]) // wellDepth
        for i, col in enumerate(minoMaxHeightCol):
            if i != cnf.gameGridX - 1:
                nextCol = minoMaxHeightCol[i+1]
                if abs(col - nextCol) >= wellDepth and col != 0 and i != 9:
                    IDependencies += abs(col - nextCol) // wellDepth

        minHeight, maxHeight = 99, 0

        for i, col in enumerate(minosInColumns):
            aggregHeight += col
            if col <= minHeight:
                minHeight = col
            if col >= maxHeight:
                maxHeight = col
        columnDiff = maxHeight - minHeight

        """
        if maxAltitude > 8:
            c1 -= maxAltitude ** 2
            c0 *= 10
            c10 *= 3
            c2 *= 5
        """
        if maxAltitude > 12:
            maxAltitude += maxAltitude * 5
            c11 = 0
            if lineClears > 0:
                c0 *= lineClearFact1


        score = 0
        lcw = tetrisWeight * 4
        if lcw > 4:
            lcw = 4
        if self.field.speedLevel < 14 and ((maxAltitude <= tetrisWeight*6) and (lineClears > 0 and lineClears < lcw)):
            score -= (15000 * tetrisWeight)

        if maxAltitude <= 5 and IDependencies == 1:
            IDependencies = 0

        if lineClears == 4:
            score += int(99999 * tetrisWeight)

        score += c0 * lineClears * maxAltitude + c1 * maxAltitude + c2 * holes * maxAltitude + c3 * roughness + c4 * columnDiff + c5 * aggregHeight + c6 * totalHolesInColumns**2 + c7 * blocksWell + c8 * center + (c9 * minosAboveHoles) + c10 * IDependencies ** 2 + c11 * highestEmptyCellCnt

        constants = [c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11]
        parametersToReturn = [lineClears, maxAltitude, holes, roughness, columnDiff, aggregHeight, totalHolesInColumns,
                              blocksWell, center, minosAboveHoles, IDependencies, highestEmptyCellCnt]
        parametersToReturn.extend([const * parametersToReturn[idx] for idx, const in enumerate(constants)])
        return score, parametersToReturn


    def computeBestMove(self, piece, positionList, numMoves=1):
        """
        Test each position in positionList for a given piece,
        and choose the best position based on its score.
        """
        pieceCopy = copy.deepcopy(piece)
        pieceId = pieceCopy.getId()
        maxScore, maxScoreIdx, maxScoreData = -9999999, 0, []
        scoreList = []

        prevContent = []
        deletedLines = []

        gameContent = [x[:] for x in self.grid.contentsLocked]

        def display():
            print("GRID---------------")
            for x in range(36, 40):
                print(gameContent[x])
            print("-------------------")


        for i, positionData in enumerate(positionList):
            # Draw piece in a copied grid.
            # TODO: undo line clears!

            deletedLines = []

            while pieceCopy.getRotation() != positionData[2]:
                pieceCopy.rotate(0)

            pieceY, pieceX = positionData[0], positionData[1]
            pieceShape = pieceCopy.getShape()
            pieceBBSize = pieceCopy.getBBSize()
            mini, maxi = cnf.gameGridY * 2, 0
            for x in range(pieceBBSize[1]):
                for y in range(pieceBBSize[0]):
                    if pieceShape[x][y] != 0:
                        if pieceX + x < mini:
                            mini = pieceX + x
                        if pieceX + x > maxi:
                            maxi = pieceX + x
                        prevContent.append((pieceX + x, pieceY + y, gameContent[pieceX + x][pieceY + y]))
                        gameContent[pieceX + x][pieceY + y] = pieceShape[x][y]

            # Remove completed lines
            clearedLines = 0
            for x in range(mini, maxi+1):
                if 0 not in gameContent[x]:
                    clearedLines += 1
                    deletedLines.append((x, gameContent[x]))
                    del gameContent[x]
                    gameContent.insert(0, [0] * cnf.gameGridX)




            # Evaluate grid obtained with this piece, and check if it's the best move available.
            score, bestData = self.evaluateGrid(gameContent, pieceId, clearedLines)
            scoreList.append((i, score, bestData))

            if score >= maxScore:
                maxScore, maxScoreIdx, maxScoreData = score, i, bestData

            # Undo changes on copied grid:
            for change in prevContent:
                gameContent[change[0]][change[1]] = change[2]

            for delLines in deletedLines:
                del gameContent[0]
                gameContent.insert(delLines[0], delLines[1])

        debugData = [positionList, maxScoreIdx]
        return positionList[maxScoreIdx], maxScore, maxScoreData, scoreList, debugData


    def getMoveSequence(self, curPiece, pos: tuple):
        """
        Generate a list containing a sequence of moves that the CPU has to execute
        in order to move the current piece to its target position 'pos'.
        """
        moveSeq = []

        """
        pieceCopy = copy.deepcopy(curPiece)
        pieceId = pieceCopy.getId()
        targetX, targetY, targetRot = pos
        print(targetX, targetY, targetRot)
        pieceCopy.setPosition((targetX, targetY))
        for x in range(targetRot):
            pieceCopy.rotate()

        pieceCurPosX, pieceCurPosY = pieceCopy.getPosition()
        pieceCurRot = pieceCopy.getRotation()
        print(pieceCurPosX, pieceCurPosY, pieceCurRot)
        print(str(self.grid.chkMinoValidPosition(pieceCopy)))

        originX = blocks.pieceSpawnX[pieceId]
        originY = blocks.pieceSpawnY[pieceId]

        print("id:", pieceId, "origin: ", originX, originY)

        while pieceCurPosX != originX or pieceCurPosY != originY:
            pieceCurPosX, pieceCurPosY = pieceCopy.getPosition()
            pieceCurRot = pieceCopy.getRotation()

            # up
            pieceCopy.setPosition((pieceCurPosX, pieceCurPosY - 1))
            if self.grid.chkMinoValidPosition(pieceCopy) and pieceCurPosY - 1 >= originY:
                print("Decreased Y successful!", pieceCurPosY - 1)
                moveSeq.append([4, 1])
                continue
            else:
                print("failed to go up.")
                pieceCopy.setPosition((pieceCurPosX, pieceCurPosY))

            # right
            pieceCopy.setPosition((pieceCurPosX + 1, pieceCurPosY))
            if self.grid.chkMinoValidPosition(pieceCopy):
                print(">> Moved right!", pieceCurPosY - 1)
                moveSeq.append([4, 1]) 
            else:
                print("failed to go right.")
                pieceCopy.setPosition((pieceCurPosX, pieceCurPosY))
            """




        piecePosX = curPiece.getPosition()[0]
        
        xDiff = piecePosX - pos[0]
        if pos[2] != 0:  # Rotate
            moveSeq.append([2, pos[2]])
        if xDiff > 0:  # Move left
            moveSeq.append([0, xDiff])
        elif xDiff < 0:  # Move right
            moveSeq.append([1, -xDiff])
        if self.slow:
            if self.field.speedLevel < 12:
                moveSeq.append([4, 22 - self.field.speedLevel])
        else:
            moveSeq.append([5, 1])  # Hard drop
        return moveSeq

    def chkMoveQueueEmpty(self):
        return self.moveQueue == []

    def setMoveSequence(self, moveSeq):
        self.moveQueue = moveSeq

    def setDebugPiece(self, piece):
        self.debugPiece = piece

    def setDebugPositions(self, posList):
        try:
            if posList is not None:
                if posList[0] is not None:
                    self.debugGhostPos = posList
        except:
            pass

    def drawDebugGhost(self):
        if self.debugWait > 0:
            self.debugWait -= 1
        else:
            self.debugWait = 2
            if self.debugPiece != self.grid.getDebugPiece():
                self.grid.setDebugPiece(self.debugPiece)
            if self.debugPiece is not None:
                self.grid.updateDebugPieceData(self.debugGhostPos[self.debugGhostIdx])
                self.debugGhostIdx += 1
                if self.debugGhostIdx >= len(self.debugGhostPos):
                    self.debugGhostIdx = 0

    def clearDebugGhost(self):
        self.grid.setDebugPiece(None)



    def processMove(self):
        if self.moveWait > 0:
            self.moveWait -= 1
        elif not self.chkMoveQueueEmpty():
            moveType = self.moveQueue[0][0]
            self.moveWait = randint(self.minWait, self.maxWait)
            if moveType == 0:  # Move left
                self.grid.moveActivePiece(0)
                self.field.lockFrames = 0
            elif moveType == 1:  # Move right
                self.grid.moveActivePiece(1)
                self.field.lockFrames = 0
            elif moveType == 2:  # CW Rotation
                self.grid.rotateActivePiece(0)
                self.field.lockFrames = 0
            elif moveType == 3:  # CCW Rotation
                self.grid.rotateActivePiece(1)
                self.field.lockFrames = 0
            elif moveType == 4:  # Soft drop
                self.field.softDrop(True)
                self.moveWait = 2
            elif moveType == 5:  # Hard drop
                self.field.hardDrop(True)
            elif moveType == 6:  # Hold
                self.field.holdPiece()
            self.moveQueue[0][1] -= 1
            if self.moveQueue[0][1] == 0:
                del self.moveQueue[0]

