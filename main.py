from grid import Grid
from randomizer import Randomizer
from field import Field
from ai import AI
import config as cnf
import visual
import fonts
import pygame
from copy import copy, deepcopy
import time
import sfx

screen = pygame.display.set_mode((cnf.screenX, cnf.screenY))
pygame.init()


running = True
slowTime = False
fastTime = False

# Init player's game and CPU's game
gameGrid = Grid((cnf.gameGridX, cnf.gameGridY))
playerField = Field(gameGrid)
randomBag = Randomizer(cnf.bagType, cnf.bagContents)
randomBag.addBag()
playerField.updateSpeedLevel(cnf.startingSpeedLv)
DASCharge, autoRepeatFrames, IRS, IHS = 0, 0, -1, False
playerGridScore, playerGridScoreDat = 0, []

cpuGrid = Grid((cnf.gameGridX, cnf.gameGridY))
# cpuGrid.addGarbage(10, 12)
cpuField = Field(cpuGrid)
cpuBag = Randomizer(cnf.bagType, cnf.bagContents)
cpuBag.addBag()
cpuField.updateSpeedLevel(cnf.startingSpeedLv)
cpuBot = AI(cpuGrid, cpuField, cnf.cpuWaitMin, cnf.cpuWaitMax, not cnf.cpuHardDrop)
cpuPositions = None
currentPiece = None
selectedPositions = None
moveSeq = []
bestMoveData = []
bestScore = 0
bestPosIdx = 0
dbgData = []
moveDataText = ['lineClears', 'maxAltitude', 'holes', 'roughness', 'columnDiff', 'aggregHeight', 'totalHolesInColumns',
                              'blocksWell', 'center', 'minosAboveHoles', 'I-dependencies', "NULL"]
cpuDebugMove = False
cpuDebugHeld = False
dbgPiece0, dbgPiece1 = None, None
debugPieceNew, debugPieceHeld = None, None
heldPos = None
newPiece = None
selectedMoveDbg = 0
garbageDbg = False
garbageMsns = 0

frameCnt = 0

startTime = time.time()


def dbgDisplayMoveData(scr, dat, x=225, y=200, align=1, dataComparison=None):
    visual.writeText(screen, "----- Move Score:", (x, y), fonts.texgyre_small, cnf.gridBkgColor, align)
    visual.writeText(screen, str(scr), (x, y+20), fonts.texgyre_small, cnf.gridBkgColor, align)
    visual.writeText(screen, "----- Move Info:", (x, y+40), fonts.texgyre_small, cnf.gridBkgColor,
                     align)
    moveI = 0
    offset = len(dat) // 2
    for i in range(len(dat) // 2):
        text = moveDataText[moveI] + ": " + str(dat[i]) + " (" + str(dat[i + offset]) + ")"
        color = cnf.gridBkgColor
        if dataComparison is not None:
            diff = dat[i + offset] - dataComparison[i + offset]
            text += " ["
            if diff > 0:
                color = (70, 189, 77)
                text += "+"
            elif diff < 0:
                color = (228, 99, 80)
            text += str(diff)+"]"
        visual.writeText(screen, text, (x, y+60 + moveI * 20),
                         fonts.texgyre_small,
                         color,
                         align)
        moveI += 1


while running:
    clock = pygame.time.Clock()
    if slowTime:
        clock.tick(1)
    elif fastTime:
        clock.tick(9999)
    else:
        clock.tick(cnf.FPS_CAP)

    if cnf.debugFrameRate:
        frameCnt += 1
        endTime = time.time()
        timeDiff = int(endTime-startTime)
        print("Frames:", frameCnt, "| Time: ", str(timeDiff)+"s", "| Avg FPS:", str(int(frameCnt/(timeDiff+0.01))))

    # Spawn pieces
    if playerField.attemptSpawn() and not gameGrid.chkGameOverFlag():
        playerField.introduceNewPiece(randomBag.pop())
        if IRS != -1 and cnf.IRSEnabled:
            gameGrid.rotateActivePiece(IRS)
            IRS = -1
        if IHS and cnf.IHSEnabled:
            playerField.holdPiece()
            IHS = False

        if not gameGrid.moveActivePiece(0, True) and not gameGrid.moveActivePiece(1, True) and not gameGrid.moveActivePiece(2, True):
            gameGrid.callGameOver()
            
    if cpuField.attemptSpawn() and cnf.displayCPUGrid and not cpuGrid.chkGameOverFlag():
        if garbageDbg:
            cpuGrid.addGarbage(garbageMsns)
            garbageDbg = False
            garbageMsns = 7
        dbgDataTemp = None
        allMoveScoresTemp = None
        bestMoveDataTemp = None
        bestPos = None
        newPiece = cpuBag.pop()
        cpuField.introduceNewPiece(newPiece)

        if not cpuGrid.moveActivePiece(0, True) and not cpuGrid.moveActivePiece(1, True) and not cpuGrid.moveActivePiece(2, True):
            cpuGrid.callGameOver()

        cpuPositions = cpuBot.generateHardDropPos(newPiece)
        curPiecePos, curScore, bestMoveDataTemp, allMoveScoresTemp, dbgDataTemp = cpuBot.computeBestMove(newPiece, cpuPositions)
        moveSeq = cpuBot.getMoveSequence(newPiece, curPiecePos)
        bestPos = curPiecePos
        dbgPiece0 = copy(newPiece)
        cpuBot.setDebugPiece(copy(newPiece))
        selectedPositions = cpuPositions
        dbgData = dbgDataTemp
        allMoveScores = allMoveScoresTemp
        bestMoveData = bestMoveDataTemp
        if cpuGrid.getHold() is None:
            # Check if next piece is better than current piece, only if there is no held piece
            nextPiece = cpuBag.getQueue(1)[0]
            nextPos = cpuBot.generateHardDropPos(nextPiece)
            nextPiecePos, nextScore, bestMoveDataTemp1, allMoveScoresTemp1, dbgDataTemp = cpuBot.computeBestMove(nextPiece, nextPos)
            if nextScore > curScore:
                moveSeq = [[6, 1]]
                bestPos = nextPiecePos
                selectedPositions = nextPos
                dbgData = dbgDataTemp
                allMoveScores = allMoveScoresTemp1
                bestMoveData = bestMoveDataTemp1
        elif cpuField.chkCanHold():
            # Check if held piece is better than the current dealt piece
            heldPiece = cpuGrid.getHold()
            dbgPiece1 = deepcopy(heldPiece)
            heldPos = cpuBot.generateHardDropPos(heldPiece)
            heldPiecePos, heldScore, heldMoveData, allMoveScoresTemp2, dbgDataTemp = cpuBot.computeBestMove(heldPiece, heldPos)
            if heldScore > curScore:
                dbgPiece0 = deepcopy(heldPiece)
                dbgPiece1 = deepcopy(newPiece)
                moveSeq = [[6, 1]]
                moveSeq.extend(cpuBot.getMoveSequence(heldPiece, heldPiecePos))
                bestPos = heldPiecePos
                cpuBot.setDebugPiece(deepcopy(heldPiece))
                selectedPositions = heldPos
                dbgData = dbgDataTemp
                allMoveScores = allMoveScoresTemp2
                bestMoveData = heldMoveData
                print("BestmoveData is temp2")

        cpuBot.setMoveSequence(moveSeq)
        bestScore = 0
        for x in range(len(bestMoveData)//2, len(bestMoveData)):
            bestScore += bestMoveData[x]





    # Gravity
    playerField.handleGravity()


    # AI

    if cpuDebugMove:
        if cpuDebugHeld:
            cpuBot.setDebugPiece(dbgPiece1)
            cpuBot.setDebugPositions([heldPos[selectedMoveDbg]])
        else:
            cpuBot.setDebugPiece(dbgPiece0)
            try:
                cpuBot.setDebugPositions([selectedPositions[selectedMoveDbg]])
            except:
                pass
        try:
            cpuBot.drawDebugGhost()
        except:
            pass
    else:
        cpuBot.clearDebugGhost()
    if not cpuDebugMove and not cpuGrid.chkGameOverFlag():
        cpuBot.processMove()

    if cnf.instantCPUPlacement and not cpuDebugMove:
        for x in range(8):
            cpuBot.processMove()
    playerGridScore, playerGridScoreDat = cpuBot.evaluateGrid(gameGrid.getLockedContents())
    if not cpuDebugMove and not cpuGrid.chkGameOverFlag():
        cpuField.handleGravity()
    # ----- Event handling -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                DASCharge = 0
                autoRepeatFrames = 0
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_UP:
                if playerField.isListeningForInputs():
                    gameGrid.rotateActivePiece(0)  # Cw rotation
                else:
                    IRS = 0
            elif event.key == pygame.K_w:
                if playerField.isListeningForInputs():
                    gameGrid.rotateActivePiece(1)  # Ccw rotation
                else:
                    IRS = 1
            elif event.key == pygame.K_SPACE:  # Hard drop
                playerField.hardDrop()
            elif event.key == pygame.K_f:
                fastTime = not fastTime  # DEBUG: Speed up internal game clock to 9999 FPS
            elif event.key == pygame.K_s:
                slowTime = not slowTime  # DEBUG: Slow internal game clock to 5 FPS
                print("--- TIME SLOW ---")
                playerField.setUpdateDisplay(True)
            elif event.key == pygame.K_g:
                if garbageDbg:
                    garbageMsns = 1
                garbageDbg = True
            elif event.key == pygame.K_d:  # DEBUG: Freeze CPU and consult every possible move it can do
                cpuDebugMove = not cpuDebugMove
                cpuDebugHeld = False
                selectedMoveDbg = dbgData[1]
                bestPosIdx = dbgData[1]
                cpuField.setUpdateDisplay(True)
            elif event.key == pygame.K_h and cpuDebugMove:
                cpuDebugHeld = not cpuDebugHeld
            elif event.key == pygame.K_LSHIFT:
                if playerField.isListeningForInputs():
                    playerField.holdPiece()
                else:
                    IHS = True
            if playerField.isListeningForInputs() and event.key == pygame.K_UP or event.key == pygame.K_w:
                # Reset lock delay after successful rotation.
                playerField.setUpdateDisplay(True)
                playerField.resetLockDelay()

    # ----- Keypress handling -----
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_DOWN]:  # Soft drop
        playerField.softDrop()
    if pressed[pygame.K_LEFT]:
        if DASCharge == 0 and playerField.isListeningForInputs():
            gameGrid.moveActivePiece(0)
            if gameGrid.moveActivePiece(0, True):
                playerField.resetLockDelay()
            playerField.setUpdateDisplay(True)
            if cpuDebugMove:
                selectedMoveDbg -= 1
                if selectedMoveDbg < 0:
                    selectedMoveDbg = len(cpuPositions) - 1
        elif DASCharge >= cnf.DAS:
            autoRepeatFrames += 1
            if autoRepeatFrames >= cnf.ARR and playerField.isListeningForInputs():
                if cpuDebugMove:
                    selectedMoveDbg -= 1
                    if selectedMoveDbg <= 0 :
                        selectedMoveDbg = len(cpuPositions) - 1
                autoRepeatFrames = 0
                gameGrid.moveActivePiece(0)
                if gameGrid.moveActivePiece(0, True):
                    playerField.resetLockDelay()
                playerField.setUpdateDisplay(True)
        DASCharge += 1
    elif pressed[pygame.K_RIGHT]:
        if DASCharge == 0 and playerField.isListeningForInputs():
            gameGrid.moveActivePiece(1)
            if gameGrid.moveActivePiece(1, True):
                playerField.resetLockDelay()
            playerField.setUpdateDisplay(True)
            if cpuDebugMove:
                selectedMoveDbg += 1
                if selectedMoveDbg >= len(cpuPositions):
                    selectedMoveDbg = 0
        elif DASCharge >= cnf.DAS:
            autoRepeatFrames += 1
            if autoRepeatFrames >= cnf.ARR and playerField.isListeningForInputs():
                if cpuDebugMove:
                    selectedMoveDbg += 1
                    if selectedMoveDbg >= len(cpuPositions):
                        selectedMoveDbg = 0
                autoRepeatFrames = 0
                gameGrid.moveActivePiece(1)
                if gameGrid.moveActivePiece(1, True):
                    playerField.resetLockDelay()
                playerField.setUpdateDisplay(True)
        DASCharge += 1

    # ----- UI ------
    if playerField.checkDisplayUpdate() or cpuField.checkDisplayUpdate():
        screen.fill(cnf.bkgColor)
        playerFieldPos = (250, 60)

        if cnf.displayPlayerGrid:
            visual.drawBackground(screen, playerFieldPos)
            visual.drawField(screen, playerFieldPos, gameGrid, playerField.getClearedLines(),
                             [playerField.getLineClearFrames()])

            # Held piece
            visual.drawPolyominoFrame(screen, (playerFieldPos[0] - 150, 70), 120, gameGrid.getHold())

            # Next queue
            minoQueue = randomBag.getQueue(cnf.nextQueue)
            for x in range(cnf.nextQueue):
                visual.drawPolyominoFrame(screen, (cnf.gameGridX * cnf.cellSizePx + playerFieldPos[0] + 30, 70 + 130 * x), 120, minoQueue[x])

            # Text
            visual.writeText(screen, "Niv. vitesse", (225, 450), fonts.texgyre, cnf.gridBkgColor, 1)
            spdLv = playerField.getSpeedLevel()
            spdStr = str(spdLv)
            if spdLv > 20:
                spdStr = "M"+str(spdLv-20)
                visual.writeText(
                    screen,
                    "("+str(cnf.masterSpeedData[spdLv-20][0]*16 + cnf.masterSpeedData[spdLv-20][1]*2)+" ms)",
                    (225, 300),
                    fonts.texgyre,
                    cnf.gridBkgColor,
                    1
                )
            visual.writeText(screen, str(spdStr), (225, 480), fonts.texgyre_num, cnf.gridBkgColor, 1)
            visual.writeText(screen, "PPS: "+str(round(playerField.getPiecesPlaced() / (time.time() - startTime), 2)), (225, 580), fonts.texgyre, cnf.gridBkgColor, 1)
            visual.writeText(screen, "Lignes", (225, 620), fonts.texgyre, cnf.gridBkgColor, 1)
            visual.writeText(screen, str(playerField.getNumClearedLines()), (225, 650), fonts.texgyre_num, cnf.gridBkgColor, 1)
            visual.writeText(screen, "Score", (225, 740), fonts.texgyre, cnf.gridBkgColor, 1)
            visual.writeText(screen, str(playerField.getScore()), (225, 770), fonts.texgyre_num, cnf.gridBkgColor, 1)
            visual.writeText(screen, "CLAVIER ET SOURIS ", (playerFieldPos[0] + (cnf.gameGridX * cnf.cellSizePx) // 2, cnf.screenY - 80),
                             fonts.texgyre, cnf.gridBkgColor, 2)
            visual.writeText(screen, "----- Move Score:", (playerFieldPos[0] - 25, 200), fonts.texgyre_small,
                             cnf.gridBkgColor, 1)
            visual.writeText(screen, str(playerGridScore), (playerFieldPos[0] - 25, 220), fonts.texgyre_small, cnf.gridBkgColor,
                             1)
            visual.writeText(screen, "----- Move Info:", (playerFieldPos[0] - 25, 240), fonts.texgyre_small,
                             cnf.gridBkgColor,
                             1)
            moveIdx = 0
            '''for i in range(0, playerGridScoreDat, 2):
                visual.writeText(screen, moveDataText[moveIdx] + ": " + str(playerGridScoreDat[i]) + "("+str(playerGridScoreDat[i+1])+")", (playerFieldPos[0] - 25, 260 + i * 20),
                                 fonts.texgyre_small,
                                 cnf.gridBkgColor,
                                 1)
                moveIdx += 1'''
            '''for i, x in enumerate(playerGridScoreDat):
                visual.writeText(screen, moveDataText[i] + ": " + str(x), (playerFieldPos[0] - 25, 260 + i * 20),
                                 fonts.texgyre_small,
                                 cnf.gridBkgColor,
                                 1)'''

        if cnf.displayCPUGrid:
            cpuFieldPos = (1050, 60)
            if not cnf.displayPlayerGrid:
                cpuFieldPos = playerFieldPos
            visual.drawBackground(screen, cpuFieldPos)
            visual.drawField(screen, cpuFieldPos, cpuGrid, cpuField.getClearedLines(), [cpuField.getLineClearFrames()], cpuField.chkInZone())
            visual.drawPolyominoFrame(screen, (cpuFieldPos[0] - 150, 70), 120, cpuGrid.getHold())
            minoQueueCPU = cpuBag.getQueue(cnf.nextQueue)
            for x in range(cnf.nextQueue):
                visual.drawPolyominoFrame(screen, (cnf.gameGridX * cnf.cellSizePx + cpuFieldPos[0] + 30, 70 + 130 * x),
                                          120, minoQueueCPU[x])
            if cpuDebugMove:
                visual.writeText(screen, "[DEBUG CPU MOVE: "+str(selectedMoveDbg)+"/"+str(len(selectedPositions)-1)+"] (Best: "+str(bestPosIdx)+")", (cpuFieldPos[0] - 25, 35), fonts.texgyre,
                                 (107, 181, 83), 2)

            visual.writeText(screen, "PPS: " + str(round(cpuField.getPiecesPlaced() / (time.time() - startTime), 2)),
                             (cpuFieldPos[0] - 25, 580), fonts.texgyre, cnf.gridBkgColor, 1)
            visual.writeText(screen, "Lignes", (cpuFieldPos[0] - 25, 620), fonts.texgyre, cnf.gridBkgColor, 1)
            visual.writeText(screen, str(cpuField.getNumClearedLines()), (cpuFieldPos[0] - 25, 650), fonts.texgyre_num,
                             cnf.gridBkgColor, 1)
            visual.writeText(screen, "Score", (cpuFieldPos[0] - 25, 740), fonts.texgyre, cnf.gridBkgColor, 1)
            visual.writeText(screen, str(cpuField.getScore()), (cpuFieldPos[0] - 25, 770), fonts.texgyre_num, cnf.gridBkgColor, 1)
            visual.writeText(screen, " CPU", (cpuFieldPos[0] + (cnf.gameGridX * cnf.cellSizePx) // 2, cnf.screenY - 80), fonts.texgyre, cnf.gridBkgColor, 2)
            dbgDisplayMoveData(bestScore, bestMoveData, cpuFieldPos[0] - 25, 200)
            if cpuDebugMove:
                try:
                    curSelMoveDbg = allMoveScores[selectedMoveDbg]
                    dbgDisplayMoveData(curSelMoveDbg[1], curSelMoveDbg[2], cpuFieldPos[0] + 600, 200, 0, bestMoveData)
                    if cpuDebugHeld and cpuField.chkCanHold():
                        curSelMoveDbg1 = allMoveScoresTemp2[selectedMoveDbg]
                        dbgDisplayMoveData(curSelMoveDbg1[1], curSelMoveDbg1[2], cpuFieldPos[0] + 600, 600, 0, bestMoveData)
                except:
                    print("something happened")
        pygame.display.flip()
        playerField.setUpdateDisplay(False)

    # ----- Lock piece -----
    if not gameGrid.chkGameOverFlag():
        playerField.handleLocking(cpuGrid, 9, 1)
    if not cpuGrid.chkGameOverFlag():
        cpuField.handleLocking(gameGrid, 5, 1)

pygame.quit()
