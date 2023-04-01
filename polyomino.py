# TODO: add wall kicks

class Polyomino:
    def __init__(self, idNum: int, color: tuple, bbSize: tuple, shapeData: list):
        """
        Creates a new polyomino with a bounding box defined by the bbSize
        tuple. shapeData is a list composed of tuples indicating which
        squares of the bounding box are full and make up the polyomino.
        """
        self.id = idNum
        self.color = color
        self.bbSize = bbSize
        self.shapeData = shapeData
        self.shape = [[0] * self.bbSize[0] for y in range(self.bbSize[1])]
        for data in shapeData:
            self.shape[data[1]][data[0]] = self.id
        self.position = [0, 0]  # upper left corner position of mino in grid.
        self.rotation = 0

    # -------- Getters and setters -----------

    # THE MOST USELESS AND CRINGE SETTERS IN EXISTENCE

    def getPosition(self) -> list:
        return self.position

    def getId(self) -> int:
        return self.id

    def setId(self, newId) -> None:
        self.id = newId

    def setShapeInt(self, n):
        for x in range(len(self.shape)):
            for y in range(len(self.shape[0])):
                if self.shape[x][y] != 0:
                    self.shape[x][y] = n

    def getColor(self) -> int:
        return self.color

    def getShape(self) -> list:
        return self.shape

    def getBBSize(self) -> tuple:
        # Returns the size of the bounding box of the polyomino.
        return self.bbSize

    def getRotation(self) -> int:
        return self.rotation

    def setPosition(self, newPos: tuple) -> None:
        self.position[0], self.position[1] = newPos[0], newPos[1]

    def __str__(self) -> str:
        s = "MINO:\n"
        for line in self.shape:
            s += str(line) + "\n"
        return s

    def rotate(self, direction=0) -> None:
        """
        Rotates the 2D list shape in clockwise or counter-clockwise direction.
        """
        # 0: clockwise, 1: counter-clockwise
        bx, by = self.bbSize[0], self.bbSize[1]
        rotatedPiece = [[0] * bx for _ in range(by)]
        if direction == 0:
            self.rotation += 1
            if self.rotation > 3:
                self.rotation = 0
        else:
            self.rotation -= 1
            if self.rotation < 0:
                self.rotation = 3
        for x in range(bx):
            for y in range(by):
                if direction == 0:
                    rotatedPiece[x][y] = self.shape[(by-1)-y][x]
                else:
                    rotatedPiece[x][y] = self.shape[y][(bx-1)-x]

        self.shape = rotatedPiece



