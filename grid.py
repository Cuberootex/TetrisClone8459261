import copy
import blocks
import config as cnf
import sfx
from random import randint

class Grid:
    def __init__(self, size=(10,20)):
        self.extraHeight = 20
        self.sizeData = size
        self.contents = [[0] * size[0] for y in range(size[1] + self.extraHeight)]
        self.contentsLocked = [[0] * size[0] for y in range(size[1] + self.extraHeight)]

        self.contentsLocked = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [8, 8, 8, 8, 8, 8, 8, 0, 0, 8],
            [8, 8, 8, 8, 8, 8, 0, 0, 8, 8],
            [8, 8, 8, 8, 0, 8, 8, 8, 8, 8],
            [8, 8, 8, 8, 0, 0, 0, 0, 8, 8],
        ]


        self.activePiece = None  # currently falling piece.
        self.debugPiece = None
        self.heldPiece = None
        self.rotationSuccess = False
        self.displayGhost = True
        self.curGarbageCol = randint(0,9)
        self.gameOver = False

    def getExtraHeight(self):
        return self.extraHeight

    def getAltitude(self):
        alt = 32767
        for i, row in enumerate(self.contents):
            if row != [0] * 10:
                alt = abs(cnf.gameGridY + self.extraHeight - i)
                break
        return alt

    def getContents(self):
        return self.contents

    def getLockedContents(self):
        return self.contentsLocked

    def drawPieceInGrid(self, piece, gridList):
        if piece is None:
            return
        pieceY, pieceX = piece.getPosition()
        pieceShape = piece.getShape()
        pieceBBSize = piece.getBBSize()
        for x in range(pieceBBSize[1]):
            for y in range(pieceBBSize[0]):
                if pieceShape[x][y] != 0:
                    if pieceY + y < 0:
                        print("uh that's illegal bro")
                    else:
                        gridList[pieceX + x][pieceY + y] = pieceShape[x][y]

    def addGarbage(self, messiness=0, lines=4):

        if randint(1,10) >= messiness:
            column = self.curGarbageCol
        else:
            self.curGarbageCol = randint(0, 9)
            column = self.curGarbageCol

        print("column: "+str(column))
        print("messiness: "+str(messiness))

        for y in range(lines):
            del self.contentsLocked[0]
            line = [8] * 10
            if messiness == 10:
                line[randint(0, 9)] = 0
            else:
                line[column] = 0
            self.contentsLocked.append(line)

    def chkPieceOOB(self, piece):
        if piece is None:
            return
        pieceX, pieceY = piece.getPosition()
        pieceShape = piece.getShape()
        pieceBBSize = piece.getBBSize()
        for x in range(pieceBBSize[1]):
            for y in range(pieceBBSize[0]):
                if pieceShape[y][x] != 0:  # WHY DOES SWAPPING Y AND X HERE FIX EVERYTHING???
                    if pieceX + x < 0:
                        return 1
                    elif pieceX + x >= cnf.gameGridX:
                        return 2
                    elif pieceY + y >= len(self.contents):
                        return 3

        return 0

    def callGameOver(self):
        self.activePiece = None
        self.debugPiece = None
        self.heldPiece = None
        self.gameOver = True

    def chkGameOverFlag(self):
        return self.gameOver

    def updateContents(self):
        if self.activePiece is not None:
            self.contents = [x[:] for x in self.contentsLocked]
            if self.displayGhost:
                self.drawGhostMino1()
            self.drawPieceInGrid(self.activePiece, self.contents)
            try:
                self.drawPieceInGrid(self.debugPiece, self.contents)
            except IndexError as e:
                print(e)
                print(self.debugPiece.getPosition())

    def __str__(self) -> str:
        self.updateContents()
        s = ""
        for line in self.contentsLocked:
            s += str(line) + "\n"
        return s

    def getActivePiece(self):
        return self.activePiece

    def getActivePieceColor(self):
        return self.activePiece.getColor()

    def setActivePiece(self, newMino, pos=(0,20)) -> None:
        self.activePiece = newMino
        if newMino is not None:
            self.activePiece.setPosition(pos)
            self.updateContents()

    def setGhostDisplay(self, state=True):
        self.displayGhost = state

    def chkMinoValidPosition(self, futureMino):
        result = True
        contentsTemp = [*self.contentsLocked]
        # Check if piece is out of bounds and/or if piece overlaps w/ another
        try:
            pieceY, pieceX = futureMino.getPosition()
            pieceShape = futureMino.getShape()
            pieceBBSize = futureMino.getBBSize()
            for y in range(pieceBBSize[1]):
                for x in range(pieceBBSize[0]):
                    if pieceShape[x][y] != 0:
                        if pieceY + y < 0 or contentsTemp[pieceX + x][pieceY + y] != 0:
                            result = False
        except IndexError:
            result = False
        return result

    def moveMino(self, mino, direction=0, testMode=False):
        # returns a tuple containing the new mino and its position unless testMode is active: then return a bool.
        # 0: left, 1: right, 2: down, 3: hard drop
        if mino is None:
            return
        else:
            futureMino = copy.deepcopy(mino)
            futureMinoPos = futureMino.getPosition()
            if direction == 2:
                futureMinoPos[1] += 1
            elif direction == 1:
                futureMinoPos[0] += 1
            elif direction == 0:
                futureMinoPos[0] -= 1

            futureMino.setPosition(tuple(futureMinoPos))
            if self.chkMinoValidPosition(futureMino) and not testMode:
                if direction == 3:
                    pass
                return (futureMino, tuple(futureMinoPos))
            elif testMode:
                return self.chkMinoValidPosition(futureMino)

    def drawGhostMino1(self):
        if self.getActivePiece() is None:
            return
        ghostMino = copy.deepcopy(self.activePiece)
        ghostMino.setShapeInt(-1)
        for x in range(cnf.gameGridY + 20 - ghostMino.getPosition()[1]):
            try:
                ghostMino = self.moveMino(ghostMino, 2)[0]
            except Exception:
                break
        self.drawPieceInGrid(ghostMino, self.contents)

    def setDebugPiece(self, piece):
        if piece is not None:
            piece.setShapeInt(-2)
        self.debugPiece = piece

    def getDebugPiece(self):
        return self.debugPiece

    def updateDebugPieceData(self, data):
        if self.debugPiece is not None:
            self.debugPiece.setPosition((data[0], data[1]))
            while data[2] != self.debugPiece.getRotation():
                self.debugPiece.rotate(0)
            self.updateContents()

    def moveActivePiece(self, direction=0, testMode=False):
        moveData = self.moveMino(self.activePiece, direction, testMode)
        if moveData is not None:
            if type(moveData) == bool:
                return moveData 
            else:
                sfx.movePieceSound()
                self.setActivePiece(moveData[0], moveData[1])

    def rotateActivePiece(self, direction=0):
        # 0: clockwise, 1: counter-c.
        self.rotationSuccess = False
        if self.getActivePiece() is None:
            return
        else:
            futureMino = copy.deepcopy(self.activePiece)
            futureMino.rotate(direction)
            if self.chkMinoValidPosition(futureMino):
                self.setActivePiece(futureMino, self.activePiece.getPosition())
                self.rotationSuccess = True
            else:
                initRotation = self.activePiece.getRotation()
                futureRotation = futureMino.getRotation()
                bbSize = futureMino.getBBSize()[0]
                originPos = futureMino.getPosition()
                kickData = self.getKickData(bbSize, initRotation, futureRotation)
                if kickData is not None:
                    for kickPos in kickData:
                        originPosCopy = copy.deepcopy(originPos)
                        newPos = copy.deepcopy(originPos)
                        newPos[0] += kickPos[0]
                        newPos[1] -= kickPos[1]
                        futureMino.setPosition(tuple(newPos))
                        if self.chkMinoValidPosition(futureMino):
                            self.setActivePiece(futureMino, tuple(newPos))
                            self.rotationSuccess = True
                            break
                        else:
                            originPos = originPosCopy
            self.updateContents()

    def getKickData(self, bbSize, state0, state1):
        # Source: https://tetris.fandom.com/wiki/SRS#Wall_Kicks
        rotationOrders = [(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 0), (0, 3)]

        if state0 == state1 == 0:
            return

        kickIndex = rotationOrders.index(tuple([state0, state1]))
        # YandereDev mode engaged
        if bbSize == 3:
            return blocks.kickData3BB[kickIndex]
        elif bbSize == 4:
            return blocks.kickData4BB[kickIndex]
        elif bbSize == 6:
            return blocks.kickData6BB[kickIndex]
        elif bbSize == 8:
            return blocks.kickData8BB[kickIndex]


    def lockCurrentPiece(self):
        actPiece = self.getActivePiece()
        if actPiece is not None:
            lockedId = actPiece.getId() * 100
            actPiece.setShapeInt(lockedId)
            self.drawPieceInGrid(actPiece, self.contentsLocked)
            self.setActivePiece(None)

    def getCompletedLines(self) -> list:
        linesToClear = []
        for idx, line in enumerate(self.contentsLocked):
            emptyCells = len(line)
            for cell in line:

                if cell != 0 and cell != 9:
                    emptyCells -= 1
            if emptyCells == 0:
                print(line)
                linesToClear.append(idx)
        return linesToClear

    def clearCompletedLines(self, linesToClear: list, inZone=False):
        for idx in linesToClear:
            if inZone:
                self.contentsLocked[idx] = [9] * cnf.gameGridX
                self.contentsLocked.append(self.contentsLocked.pop(idx))
            else:
                del self.contentsLocked[idx]
                self.contentsLocked.insert(0, [0] * self.sizeData[0])
            
    def setHold(self):
        temp, tempId = None, 0
        if self.heldPiece is not None:
            temp = self.heldPiece
            tempId = temp.getId()
        self.heldPiece = self.activePiece
        while self.heldPiece.getRotation() != 0:
            self.heldPiece.rotate(0)
        if temp is not None:
            self.setActivePiece(temp, (blocks.pieceSpawnX[tempId], blocks.pieceSpawnY[tempId]))
        else:
            self.setActivePiece(None)

    def getHold(self):
        return self.heldPiece

