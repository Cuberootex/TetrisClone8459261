import config as cnf
import blocks
import sfx

class Field:
    def __init__(self, grid):
        self.grid = grid
        self.speedLevel = 1
        self.softDropDebounce = 0
        self.gravityDebounce = 0
        self.gravityDebounceMax = 0
        self.gravityCells = 1
        self.lockResets = 0
        self.lockFrames = 0
        self.lockDelay = cnf.lockDelay
        self.lineClearDelay = cnf.LCD
        self.pieceWaitFrames = 0
        self.lineClearFrames = 0
        self.clearedLines = []
        self.numClearedLines = 0
        self.score = 0
        self.piecesPlaced = 0
        self.listenForInputs = True
        self.canSpawnPiece = True
        self.canHold = True
        self.updateDisplay = True
        self.inZone = False
        
    def isListeningForInputs(self):
        return self.listenForInputs
    
    def setListenForInputs(self, new):
        self.listenForInputs = new
    
    def setUpdateDisplay(self, new):
        self.updateDisplay = new
        
    def getLineClearFrames(self):
        return self.lineClearFrames

    def getPiecesPlaced(self):
        return self.piecesPlaced

    def getClearedLines(self):
        return self.clearedLines
        
    def checkDisplayUpdate(self):
        return self.updateDisplay
    
    def chkCanIntroducePiece(self):
        return self.grid.getActivePiece() is None and self.canSpawnPiece

    def chkAREValid(self):
        return self.pieceWaitFrames > cnf.ARE

    def chkCanHold(self):
        return self.canHold

    def increaseARE(self):
        self.pieceWaitFrames += 1
        
    def attemptSpawn(self):
        if self.chkCanIntroducePiece():
            if self.chkAREValid():
                return True
            else:
                self.increaseARE()
                return False
            
    def resetLockDelay(self):
        if self.lockResets < cnf.maxLockResets and self.grid.rotationSuccess:
            self.lockResets += 1
            self.lockFrames = 0
    
    def introduceNewPiece(self, newPiece):
        self.listenForInputs = True
        self.clearedLines = []
        self.lineClearFrames = 0
        self.pieceWaitFrames = 0
        self.lockResets = 0
        newPieceId = newPiece.getId()
        self.grid.setActivePiece(newPiece, (blocks.pieceSpawnX[newPieceId], blocks.pieceSpawnY[newPieceId]))
        self.setUpdateDisplay(True)
                
    def handleGravity(self):
        if self.grid.getActivePiece() is not None:
            if self.gravityDebounce > 0:
                self.gravityDebounce -= 1
            else:
                for x in range(self.gravityCells):
                    self.grid.moveActivePiece(2)
                self.gravityDebounce = self.gravityDebounceMax
                self.setUpdateDisplay(True)

    def updateSpeedLevel(self, newLv):
        if 0 <= newLv <= 20:
            self.speedLevel = newLv
            self.gravityDebounceMax, self.gravityCells = cnf.speedData[newLv]
        elif newLv > 20:
            self.speedLevel = newLv
            self.gravityDebounceMax, self.gravityCells = (0, 20)
            self.lockDelay, self.lineClearDelay = cnf.masterSpeedData[newLv - 20][0], cnf.masterSpeedData[newLv - 20][1]
            cnf.DAS = cnf.masterSpeedData[newLv - 20][2]
            print(self.lockDelay, self.lineClearDelay)

    def getSpeedLevel(self):
        return self.speedLevel

    def getGravDebounce(self):
        return self.gravityDebounceMax

    def getNumClearedLines(self):
        return self.numClearedLines
            
    def hardDrop(self, isBot=False):
        if self.listenForInputs or isBot:
            self.listenForInputs = False
            while self.grid.moveActivePiece(2, True):
                self.addScore(2)
                self.grid.moveActivePiece(2)
            self.lockFrames = 999

            self.setUpdateDisplay(True)

    def softDrop(self, ignoreDebounce=False):
        if self.softDropDebounce > 0 and not ignoreDebounce:
            self.softDropDebounce -= 1
        if self.softDropDebounce == 0 or ignoreDebounce:
            self.softDropDebounce = cnf.SDS
            self.gravityDebounce = self.getGravDebounce()
            if self.grid.moveActivePiece(2, True):
                self.grid.moveActivePiece(2)
                self.addScore(1)
            self.setUpdateDisplay(True)
    
    def holdPiece(self):
        if self.grid.getActivePiece() is not None and self.canHold:
            self.grid.setHold()
            self.lockFrames = 0
            self.canHold = False
            self.setUpdateDisplay(True)

    def handleLocking(self, opponentGrid=None, garbageSentMessiness=1, garbageMult=1):
        if not self.grid.moveActivePiece(2, True) and self.listenForInputs:
            self.lockFrames += 1
        elif self.lockResets < cnf.maxLockResets and self.lockFrames > 0:
            self.lockFrames -= 1
        if self.lockFrames > self.lockDelay and self.lineClearFrames == 0 or cnf.LCD == 0 and self.lockFrames != 0:
            self.grid.lockCurrentPiece()
            self.piecesPlaced += 1
            self.lockFrames = 0
            self.canHold = True
            self.clearedLines = self.grid.getCompletedLines()
            clears = len(self.clearedLines)
            if clears > 0:
                self.refreshSpeedLevel()
                self.numClearedLines += clears
                # -- Scoring (lines only) --
                # TODO: implement B2B, T-Spin checks, mini t-spins & combos
                clearBonus = [100, 300, 500, 800, 1000, 1200, 1500, 2000, 2500, 3000, 4000, 6000]
                self.addScore(clearBonus[clears - 1] * self.getSpeedLevel())
                self.lineClearFrames = 1
                self.listenForInputs = False
                self.canSpawnPiece = False
                self.setUpdateDisplay(True)

                if opponentGrid is not None:
                    opponentGrid.addGarbage(garbageSentMessiness, int(clears * garbageMult))


        if 0 < self.lineClearFrames < self.lineClearDelay or self.lineClearFrames == self.lineClearDelay == 1 or cnf.LCD == 0:
            self.updateDisplay = True
            self.lineClearFrames += 1
            if self.lineClearFrames >= self.lineClearDelay or cnf.LCD == 0 or self.inZone:
                clears = len(self.grid.getCompletedLines())
                self.grid.clearCompletedLines(self.clearedLines, self.inZone)
                self.canSpawnPiece = True
                alt = self.grid.getAltitude()
                if alt < 17:
                    #self.grid.addGarbage(10, 1)
                    pass


    def chkInZone(self):
        return self.inZone

    def refreshSpeedLevel(self, limit=cnf.speedLvCap):
        newLv = self.numClearedLines // cnf.speedLvLines
        if newLv > limit:
            newLv = limit
        elif newLv < cnf.startingSpeedLv:
            newLv = cnf.startingSpeedLv
        self.updateSpeedLevel(newLv)

    def addScore(self, amount):
        self.score += amount

    def getScore(self):
        return self.score
