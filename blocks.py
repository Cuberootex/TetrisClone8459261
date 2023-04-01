from polyomino import Polyomino
from copy import deepcopy
import config as cnf
from math import floor

# col, line
I_mino = Polyomino(1, cnf.tetColors[1], (4, 4), [(0, 1), (1, 1), (2, 1), (3, 1)])
J_mino = Polyomino(2, cnf.tetColors[2], (3, 3), [(0, 0), (0, 1), (1, 1), (2, 1)])
L_mino = Polyomino(3, cnf.tetColors[3], (3, 3), [(2, 0), (0, 1), (1, 1), (2, 1)])
O_mino = Polyomino(4, cnf.tetColors[4], (2, 2), [(0, 0), (0, 1), (1, 0), (1, 1)])
S_mino = Polyomino(5, cnf.tetColors[5], (3, 3), [(0, 1), (1, 1), (1, 0), (2, 0)])
T_mino = Polyomino(6, cnf.tetColors[6], (3, 3), [(0, 1), (1, 0), (1, 1), (2, 1)])
Z_mino = Polyomino(7, cnf.tetColors[7], (3, 3), [(0, 0), (1, 0), (1, 1), (2, 1)])

garbageMino = Polyomino(8, cnf.tetColors[8], (1, 1), [(0, 0)])
zoneMino = Polyomino(9, cnf.tetColors[9], (1, 1), [(0, 0)])

trimino_I = Polyomino(10, cnf.tetColors[1], (3, 3), [(0, 1), (1, 1), (2, 1)])
trimino_V = Polyomino(11, cnf.tetColors[2], (2, 2), [(0, 0), (0, 1), (1, 1)])
trimino_2 = Polyomino(12, cnf.tetColors[7], (3, 3), [(0, 0), (1, 1), (2, 1)])
trimino_3 = Polyomino(13, cnf.tetColors[5], (3, 3), [(0, 1), (1, 1), (2, 0)])
trimino_4 = Polyomino(14, cnf.tetColors[6], (3, 3), [(0, 1), (1, 0), (2, 1)])
trimino_V2 = Polyomino(15, cnf.tetColors[3], (2, 2), [(0, 0), (0, 1), (1, 0)])
trimino_5 = Polyomino(16, cnf.tetColors[4], (3, 3), [(0, 0), (1, 1), (2, 2)])

giant_I = Polyomino(17, cnf.tetColors[1], (8, 8),
                    [
                        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),
                        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3)
                    ])
giant_J = Polyomino(18, cnf.tetColors[2], (6, 6),
                    [
                        (0, 0), (1, 0), (0, 1), (1, 1),
                        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
                        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3)
                    ])
giant_L = Polyomino(19, cnf.tetColors[3], (6, 6),
                    [
                                        (4, 0), (5, 0), (4, 1), (5, 1),
                        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
                        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3)
                    ])

giant_O = Polyomino(20, cnf.tetColors[4], (4, 4),
                    [
                        (0, 0), (1, 0), (2, 0), (3, 0),
                        (0, 1), (1, 1), (2, 1), (3, 1),
                        (0, 2), (1, 2), (2, 2), (3, 2),
                        (0, 3), (1, 3), (2, 3), (3, 3)
                    ])

giant_S = Polyomino(21, cnf.tetColors[5], (6, 6),
                    [
                        (4, 0), (5, 0), (4, 1), (5, 1),
                        (2, 0), (3, 0), (2, 1), (3, 1),
                        (2, 2), (3, 2), (2, 3), (3, 3),
                        (0, 2), (1, 2), (0, 3), (1, 3),
                    ])

giant_T = Polyomino(22, cnf.tetColors[6], (6, 6),
                    [
                        (4, 2), (5, 2), (4, 3), (5, 3),
                        (2, 0), (3, 0), (2, 1), (3, 1),
                        (2, 2), (3, 2), (2, 3), (3, 3),
                        (0, 2), (1, 2), (0, 3), (1, 3),
                    ])

giant_Z = Polyomino(23, cnf.tetColors[7], (6, 6),
                    [
                        (0, 0), (1, 0), (0, 1), (1, 1),
                        (2, 0), (3, 0), (2, 1), (3, 1),
                        (2, 2), (3, 2), (2, 3), (3, 3),
                        (4, 2), (5, 2), (4, 3), (5, 3),
                    ])

blockIdList = [
    None,
    I_mino, J_mino, L_mino, O_mino, S_mino, T_mino, Z_mino, garbageMino,  # 1-7
    zoneMino,
    trimino_I, trimino_V, trimino_2, trimino_3, trimino_4, trimino_V2, trimino_5,
    giant_I, giant_J, giant_L, giant_O, giant_S, giant_T, giant_Z
]


# piece spawn X:
pieceSpawnX = [
    0,
    3, 3, 3, 4, 3, 3, 3,  # Tetriminos (I, J, L, O, S, T, Z)
    3, 4, 3, 3, 3, 3, 3,  # Triminos (I, V, 2, 3, 4, V2, 5)
    1, 2, 2, 3, 2, 2, 2, 2 # Giant pieces
]
pieceSpawnY = [
    0,
    19, 20, 20, 20, 20, 20, 20,  # Tetriminos (I, J, L, O, S, T, Z)
    19, 20, 20, 20, 20, 20, 20,  # Triminos (I, V, 2, 3, 4, V2, 5)
    18, 19, 19, 19, 19, 19, 19, 19
]

for i, v in enumerate(pieceSpawnY):
    pieceSpawnY[i] = v - 2

for i in range(len(pieceSpawnX)):
    newX = floor(cnf.gameGridX * pieceSpawnX[i] / 10)
    pieceSpawnX[i] = newX

if pieceSpawnX[1] == 1 and cnf.gameGridX == 4:
    pieceSpawnX[1] = 0


# Wall Kick Data
# Source: https://tetris.fandom.com/wiki/SRS#Wall_Kicks

def multKickData(originalData, fact=2):
    newData = deepcopy(originalData)
    for i, data in enumerate(originalData):
        for j, tup in enumerate(data):
            newData[i][j] = (fact * tup[0], fact * tup[1])
    return newData


kickData3BB = [
            [(-1, 0), (-1, 1), (0,-2), (-1,-2)],  # 0>>1
            [( 1, 0), ( 1,-1), (0, 2), ( 1, 2)],  # 1>>0
            [( 1, 0), ( 1,-1), (0, 2), ( 1, 2)],  # 1>>2
            [(-1, 0), (-1, 1), (0,-2), (-1,-2)],  # 2>>1
            [( 1, 0), ( 1, 1), (0,-2), ( 1,-2)],  # 2>>3
            [(-1, 0), (-1,-1), (0, 2), (-1, 2)],  # 3>>2
            [(-1, 0), (-1,-1), (0, 2), (-1, 2)],  # 3>>0
            [( 1, 0), ( 1, 1), (0,-2), ( 1,-2)],  # 0>>3
         ]

kickData4BB = [
            [(-2, 0), ( 1, 0), (-2,-1), ( 1, 2)],  # 0>>1
            [( 2, 0), (-1, 0), ( 2, 1), (-1,-2)],  # 1>>0
            [(-1, 0), ( 2, 0), (-1, 2), ( 2,-1)],  # 1>>2
            [( 1, 0), (-2, 0), ( 1,-2), (-2, 1)],  # 2>>1
            [( 2, 0), (-1, 0), ( 2, 1), (-1,-2)],  # 2>>3
            [(-2, 0), ( 1, 0), (-2,-1), ( 1, 2)],  # 3>>2
            [( 1, 0), (-2, 0), ( 1,-2), (-2, 1)],  # 3>>0
            [(-1, 0), ( 2, 0), (-1, 2), ( 2,-1)],  # 0>>3
        ]

kickData6BB = multKickData(kickData3BB, 2)
kickData8BB = multKickData(kickData4BB, 2)

