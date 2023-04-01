from random import choice, shuffle
import blocks

class Randomizer:
    def __init__(self, rndType=0, bagContent=0):
        """
        Creates a randomizer for the game, responsible for dealing out polyominoes.
        """
        self.rndType = rndType  # 0: '7-bag', 1: Random
        self.bagContent = bagContent  # 0: standard Tetrominoes, 1: Triminoes, 2: Giant Pieces
        self.queue = []

    def addBag(self):
        # bag is incomplete
        bags = [
            [blocks.I_mino, blocks.J_mino, blocks.L_mino, blocks.O_mino, blocks.S_mino, blocks.T_mino, blocks.Z_mino],
            [blocks.trimino_I, blocks.trimino_I, blocks.trimino_V, blocks.trimino_2, blocks.trimino_3, blocks.trimino_4,
             blocks.trimino_V2, blocks.trimino_5],
            [blocks.giant_I, blocks.giant_J, blocks.giant_L, blocks.giant_O, blocks.giant_S, blocks.giant_T, blocks.giant_Z]
        ]
        pieces = bags[self.bagContent]
        if self.rndType == 0:
            shuffle(pieces)
            self.queue.extend(pieces)
        elif self.rndType == 1:
            for x in range(10):
                self.queue.append(choice(pieces))
        else:
            self.queue.extend([blocks.S_mino, blocks.I_mino] * 8)

    def getQueue(self, length):
        return self.queue[0:length]

    def pop(self, forcePiece=None):
        if len(self.queue) < 7:
            self.addBag()
        if forcePiece != None:
            return forcePiece
        else:
            return self.queue.pop(0)
