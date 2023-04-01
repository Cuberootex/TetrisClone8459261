import config as cnf
import pygame

import fonts
import utils
import blocks
import time
from math import ceil


def drawBackground(screen, corner):
    # Game field: border and background
    gridSize = (cnf.cellSizePx * cnf.gameGridX, cnf.cellSizePx * cnf.gameGridY)
    pygame.draw.rect(screen, cnf.gridBorderColor,
                     pygame.Rect(utils.addTuples(corner, (-4, -4)), utils.addTuples(gridSize, (8, 8))))
    pygame.draw.rect(screen, cnf.gridBkgColor,
                     pygame.Rect(corner, gridSize))


def drawPolyominoFrame(screen, pos: tuple, size: int, piece=None):
    frame = pygame.Rect(pos, (size,) * 2)
    pygame.draw.rect(screen, cnf.gridBkgColor, frame)
    pygame.draw.rect(screen, cnf.gridBorderColor, frame, 2)
    if piece is None:
        return
    pieceBBSize = piece.getBBSize()
    shape = piece.getShape()
    leftCorner = (0, 0)
    margin = 0.7
    if pieceBBSize[0] % 4 == 0:
        margin = 0.85
    if pieceBBSize[0] % 2 == 0 and pieceBBSize[1] % 2 == 0 and [0] * pieceBBSize[0] not in shape:
        pieceBBSize = (pieceBBSize[0] + 2, pieceBBSize[1] + 2)
        leftCorner = (1, 1)
        margin = 0.85

    cellSizePx = ceil(size / pieceBBSize[0] * margin)
    for y in range(pieceBBSize[1]):
        for x in range(pieceBBSize[0]):
            cellPos = (pos[0] + size * ((1 - margin) / 2) + x * cellSizePx, pos[1] + size * ((1 - margin) / 2) + y * cellSizePx)
            cell = pygame.Rect(cellPos, (cellSizePx,) * 2)
            pygame.draw.rect(screen, cnf.cellBorderColor, cell, 1)
            if x >= leftCorner[0] and y >= leftCorner[1]:
                idx1, idx2 = y-leftCorner[0], x-leftCorner[0]
                if idx1 < len(shape[0]) and idx2 < len(shape[0]):
                    if shape[y-leftCorner[0]][x-leftCorner[0]] != 0:
                        pygame.draw.rect(screen, piece.getColor(), cell)
                        pygame.draw.rect(screen, cnf.minoBorderColor, cell, 1)


def writeText(screen, text, pos, font, color=(255,255,255), align=0):
    text = font.render(text, True, color)
    textRect = text.get_rect()
    if align == 1:
        textRect.topright = pos
    elif align == 2:
        textRect.center = pos
    else:
        textRect.topleft = pos
    screen.blit(text, textRect)


def drawField(screen, corner, gameGrid, clearedLines, frameData, inZone=False, debugIdx=False):
    gameContents = gameGrid.getContents()
    lineClearFrameCnt = frameData[0]

    cellSize = (cnf.cellSizePx, cnf.cellSizePx)
    for y in range(cnf.gameGridY + cnf.renderedCellsAbove):
        for x in range(cnf.gameGridX):
            hideCell = False
            cellPos = (x * cnf.cellSizePx + corner[0], (y - cnf.renderedCellsAbove) * cnf.cellSizePx + corner[1])
            cell = pygame.Rect(cellPos, cellSize)
            if y >= cnf.renderedCellsAbove:
                pygame.draw.rect(screen, cnf.cellBorderColor, cell, 1)
            cellContent = gameContents[y+20-cnf.renderedCellsAbove][x]
            cellWasMult = False

            if cellContent != 0:
                if gameGrid.chkGameOverFlag():
                    cellContent = -3
                if cellContent >= 100:
                    if cnf.hideField:
                        if int(time.time()) % cnf.hideTime != 0:
                            hideCell = True
                        else:
                            cellContent = cellContent // 100

                    else:
                        cellContent = cellContent // 100
                        cellWasMult = True

                if y+20 - cnf.renderedCellsAbove in clearedLines and not inZone:
                    pygame.draw.rect(screen, (255 - lineClearFrameCnt * 4,) * 3, cell)
                    pygame.draw.rect(screen, (255 - lineClearFrameCnt * 2,) * 3, cell, 1)
                elif cellContent > 0:
                    if not hideCell:
                        pygame.draw.rect(screen, blocks.blockIdList[cellContent].getColor(), cell)
                        pygame.draw.rect(screen, cnf.minoBorderColor, cell, 1) # Mino border
                else:
                    if cellContent == -2:
                        pygame.draw.rect(screen, (230, 120, 120), cell, 5)  # Ghost mino border
                    elif cellContent == -1:
                        pygame.draw.rect(screen, cnf.minoBorderColor + (200,), cell, 5)  # Ghost mino border
                    else:
                        pygame.draw.rect(screen, (117, 117, 144), cell)
                        pygame.draw.rect(screen, cnf.minoBorderColor, cell,1)
            if debugIdx:
                extra = 1
                if cellWasMult:
                    extra = 100
                writeText(screen, str(cellContent * extra), cellPos, fonts.texgyre_small, (0, 0, 0), 0)
