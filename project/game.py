from settings import *
import random
import datetime

### remaining features:
# checkLineClears()
# generateTetromino()
# compute score, level, etc.
# collision checker
# hard drop action
# others..

class GameInfo:
    def __init__(self):
        self.playerScore = 0
        self.gameLevel = 1
        self.elapsedTime = datetime.time(0, 0, 0)

    def updateGameInfo(self):
        self.elapsedTime = datetime.datetime.now().time()

class Playfield:
    def __init__(self, info):
        self.info = info
        self.blockMatrix = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.currentPiece = Tetromino(self)
        self.nextPiece = Tetromino(self)
        self.fallSpeed = FRAMEPERSEC / 100
        self.fallTimer = 0

    # generate again after 1st line clearing
    def generateTetromino(self):
        self.currentPiece = self.nextPiece
        self.nextPiece = Tetromino(self)

    def moveTetromino(self, action):
        #if no piece falling
        if not self.currentPiece:
            return

        dx, dy = 0, 0
        if action == "left":
            dx = -1
        elif action == "right":
            dx = 1
        elif action == "down":
            dy = 1
        elif action == "rotate_left":
            self.currentPiece.rotate(-1)
        elif action == "rotate_right":
            self.currentPiece.rotate(1)
        elif action == "hard_drop":
            # HARD DROP FEATURE HERE
            return

        # if moves
        new_x = self.currentPiece.coord[0] + dx
        new_y = self.currentPiece.coord[1] + dy

        ## CHECK BOUNDS COLLISION (MOVE THIS TO COLLISION FEATURE)
        # x: 0 to no. columns minus shape width + 1

        if self.check_collision(new_x, new_y):
            return

        self.currentPiece.coord[0] = new_x
        self.currentPiece.coord[1] = new_y


    # handles falling (called by main)
    def update(self, dt): 
        self.fallTimer += dt 
        if self.fallTimer >= self.fallSpeed * 1000: 
            self.fallTimer = 0 
            self.moveTetromino("down")

    def check_collision(self, new_x, new_y):
        for dx, dy in self.currentPiece.getShapeArray():
            new_x+=dx
            new_y+=dy
            if new_x < 0 or >= COLUMNS or 0 > new_y >= ROWS:
                return True

        return False

class Tetromino:
    def __init__(self, field):
        self.field = field # playfield object
        # middle spawn column/2
        self.coord = [COLUMNS // 2 - 2, 0]
        # index of orientation inside ShapeList
        self.rotation = 0

        #shapeList disctionary
        self.ShapeList = {
            "S": {
                "color": GREEN,
                "rotations": [
                    [(0,1), (0,2), (1,0), (1,1)],
                    [(0,0), (1,0), (1,1), (2,1)]
                ]
            },
            "Z": {
                "color": RED,
                "rotations": [
                    [(0,0), (0,1), (1,1), (1,2)],
                    [(0,1), (1,0), (1,1), (2,0)]
                ]
            },
            "J": {
                "color": BLUE,
                "rotations": [
                    [(0,0), (1,0), (1,1), (1,2)],
                    [(0,0), (0,1), (1,0), (2,0)],
                    [(1,0), (1,1), (1,2), (2,2)],
                    [(0,1), (1,1), (2,0), (2,1)]
                ]
            },
            "L": {
                "color": ORANGE,
                "rotations": [
                    [(0,2), (1,0), (1,1), (1,2)],
                    [(0,0), (1,0), (2,0), (2,1)],
                    [(1,0), (1,1), (1,2), (2,0)],
                    [(0,0), (0,1), (1,1), (2,1)]
                ]
            },
            "T": {
                "color": PURPLE,
                "rotations": [
                    [(0,1), (1,0), (1,1), (1,2)],
                    [(0,0), (1,0), (1,1), (2,0)],
                    [(1,0), (1,1), (1,2), (2,1)],
                    [(0,1), (1,0), (1,1), (2,1)]
                ]
            },
            "O": {
                "color": YELLOW,
                "rotations": [
                    [(0,0), (0,1), (1,0), (1,1)]
                ]
            },
            "I": {
                "color": CYAN,
                "rotations": [
                    [(0,0), (1,0), (2,0), (3,0)],
                    [(0,0), (0,1), (0,2), (0,3)]
                ]
            },
        }

        # each class randomly chooses its shape & color
        # .keys() returns shape code S,Z,J,L,T,O,I
        self.shapeType = random.choice(list(self.ShapeList.keys()))
        self.color = self.ShapeList[self.shapeType]["color"]

    # returns the shape array
    def getShapeArray(self):
        return self.ShapeList[self.shapeType]["rotations"][self.rotation]

    # changes the rotation orientation
    # in circular manner
    def rotate(self, direction):
        n = len(self.ShapeList[self.shapeType]["rotations"])
        self.rotation = (self.rotation + direction) % n
