from settings import *
import random
import datetime

### remaining features:
# checkLineClears()
# compute score, level, etc.
# hard drop action
# Rotation collisions
# others..

class GameInfo:
    def __init__(self):
        self.playerScore = 0
        self.gameLevel = 1
        self.elapsedTime = datetime.time(0, 0, 0)

    def updateGameInfo(self):
        self.elapsedTime = datetime.datetime.now().time()

    def updateScore(self, lines_cleared):
        if lines_cleared == 1:
            self.playerScore+=40
        elif lines_cleared == 2:
            self.playerScore+=100
        elif lines_cleared == 3:
            self.playerScore+=300
        elif lines_cleared == 4:
            self.playerScore+=1200

class Playfield:
    def __init__(self, info):
        self.info = info
        self.blockMatrix = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        # Blocks fall every 36 frames
        self.fallSpeed = 36 / FRAMEPERSEC
        self.fallTimer = 0
        self.bag = list(Tetromino.ShapeList.keys())
        random.shuffle(self.bag)
        self.currentPiece = Tetromino(self.bag.pop())
        self.nextPiece = Tetromino(self.bag.pop())

    # generate again after 1st line clearing
    def generateTetromino(self):
        if not self.bag:
            self.bag = list(Tetromino.ShapeList.keys())
            random.shuffle(self.bag)
        self.currentPiece = self.nextPiece
        self.nextPiece = Tetromino(self.bag.pop())
        # Check game over
        if self.check_collision(self.currentPiece.coord[0], self.currentPiece.coord[1], self.currentPiece.getShapeArray()):
            print("GAME OVER")
            exit()

    def moveTetromino(self, action):
        #if no piece falling
        if not self.currentPiece:
            return

        dx, dy = 0, 0
        if action == MOVE_LEFT:
            dx = -1
        elif action == MOVE_RIGHT:
            dx = 1
        elif action == MOVE_DOWN:
            dy = 1
            self.fallTimer = 0
        # Rotating resets falltimer
        elif action == ROTATE_LEFT:
            self.rotation_collision(-1)
            return
        elif action == ROTATE_RIGHT:
            self.rotation_collision(1)
            return
        elif action == HARD_DROP:
            # HARD DROP FEATURE HERE
            return
        else:
            return

        ## CHECK BOUNDS COLLISION 
        if self.check_collision(self.currentPiece.coord[0] + dx, self.currentPiece.coord[1] + dy, self.currentPiece.getShapeArray()):
            return

        self.currentPiece.coord[0] += dx
        self.currentPiece.coord[1] += dy


    # handles falling and checking for block placement (called by main)
    def update(self, dt, colorMatrix): 
        self.fallTimer += dt 
        if self.fallTimer >= self.fallSpeed * 1000: 
            self.fallTimer = 0 
            _coords = self.currentPiece.coord

            # Check if we will place block by checking collisions from coords (x,y+1)
            if self.check_collision(_coords[0], _coords[1]+1, self.currentPiece.getShapeArray()):
                self.place_block(_coords, colorMatrix)
                lines_cleared = self.check_line_clears(colorMatrix)
                self.info.updateScore(lines_cleared)
                self.generateTetromino()
            else:
                self.moveTetromino(MOVE_DOWN)

    # Returns true if a boundary or block collision was dected, false otherwise
    def check_collision(self, new_x, new_y, shape_array):
        for dx, dy in shape_array:
            dx+=new_x
            dy+=new_y

            if dx < 0 or dx >= COLUMNS or dy < 0 or dy >= ROWS or self.blockMatrix[dy][dx] > 0:
                return True
        return False

    # checks for collisions whrn rotating, adjusts coordinates to fit rotation
    def rotation_collision(self, rotation):
        new_x = self.currentPiece.coord[0]
        new_y = self.currentPiece.coord[1]
        shape_array = self.currentPiece.getNewOrientation(rotation)
        for dx, dy in shape_array:
            dx+=self.currentPiece.coord[0]
            dy+=self.currentPiece.coord[1]
            
            # make corrections to coordinates if rotations causes collisions
            if dx < 0:
                new_x+=1
            elif dx >= COLUMNS:
                new_x-=1
            elif dy < 0:
                new_y+=1
            elif dy >= ROWS:
                new_y-=1
            elif self.blockMatrix[dy][dx] > 0:
                new_y-=1

        # check if new coordinates don't collide then we rotate
        if not self.check_collision(new_x, new_y, shape_array):
            self.currentPiece.coord[0] = new_x
            self.currentPiece.coord[1] = new_y
            self.currentPiece.rotate(rotation)
            self.fallTimer = 0  # reset timer when rotating

    # places the blocks of current tetromino on block matrix and the color matrix
    def place_block(self, coords, colorMatrix):
        for x, y in self.currentPiece.getShapeArray():
            self.blockMatrix[coords[1] + y][coords[0] + x] = 1
            colorMatrix[coords[1] + y][coords[0] + x] = self.currentPiece.color

    # Called every time board gets updated
    def check_line_clears(self, colorMatrix):
        # Check for any completed line from the y pos of current piece up to y+4
        line_clears = 0
        for y in range(self.currentPiece.coord[1], self.currentPiece.coord[1]+4):
            if y >= ROWS:
                continue
            if all([x == 1 for x in self.blockMatrix[y]]):
                self.blockMatrix.pop(y)
                colorMatrix.pop(y)
                self.blockMatrix.insert(0, [0 for _ in range(COLUMNS)])
                colorMatrix.insert(0, [BLACK for _ in range(COLUMNS)])
                line_clears+=1

        return line_clears


class Tetromino:
    #shapeList disctionary
    ShapeList = {
        "S": {
            "color": GREEN,
            "rotations": [
                [(1,0), (2,0), (0,1), (1,1)],
                [(1,0), (1,1), (2,1), (2,2)],
                [(1,1), (2,1), (0,2), (1,2)],
                [(0,0), (0,1), (1,1), (1,2)]
            ]
        },
        "Z": {
            "color": RED,
            "rotations": [
                [(0,0), (1,0), (1,1), (2,1)],
                [(2,0), (1,1), (2,1), (1,2)],
                [(0,1), (1,1), (1,2), (2,2)],
                [(1,0), (0,1), (1,1), (0,2)]
            ]
        },
        "J": {
            "color": BLUE,
            "rotations": [
                [(0,0), (0,1), (1,1), (2,1)],
                [(1,0), (2,0), (1,1), (1,2)],
                [(0,1), (1,1), (2,1), (2,2)],
                [(1,0), (1,1), (0,2), (1,2)]
            ]
        },
        "L": {
            "color": ORANGE,
            "rotations": [
                [(2,0), (0,1), (1,1), (2,1)],
                [(1,0), (1,1), (1,2), (2,2)],
                [(0,1), (1,1), (2,1), (0,2)],
                [(0,0), (1,0), (1,1), (1,2)]
            ]
        },
        "T": {
            "color": PURPLE,
            "rotations": [
                [(1,0), (0,1), (1,1), (2,1)],
                [(1,0), (1,1), (2,1), (1,2)],
                [(0,1), (1,1), (2,1), (1,2)],
                [(1,0), (0,1), (1,1), (1,2)]
            ]
        },
        "O": {
            "color": YELLOW,
            "rotations": [
                [(1,0), (2,0), (1,1), (2,1)],
                [(1,0), (2,0), (1,1), (2,1)],
                [(1,0), (2,0), (1,1), (2,1)],
                [(1,0), (2,0), (1,1), (2,1)]
            ]
        },
        "I": {
            "color": CYAN,
            "rotations": [
                [(0,1), (1,1), (2,1), (3,1)],
                [(2,0), (2,1), (2,2), (2,3)],
                [(0,2), (1,2), (2,2), (3,2)],
                [(1,0), (1,1), (1,2), (1,3)]
            ]
        },
    }

    def __init__(self, shape):
        # middle spawn column/2
        self.coord = [COLUMNS // 2 - 2, 0]
        # index of orientation inside ShapeList
        self.rotation = 0
        # each class randomly chooses its shape & color
        # .keys() returns shape code S,Z,J,L,T,O,I
        self.shapeType = shape
        self.color = Tetromino.ShapeList[self.shapeType]["color"]

    # returns the shape array
    def getShapeArray(self):
        return Tetromino.ShapeList[self.shapeType]["rotations"][self.rotation]

    # changes the rotation orientation
    # in circular manner
    def rotate(self, direction):
        self.rotation = (self.rotation + direction) % 4

    # get rotation info without rotating tetromino
    def getNewOrientation(self, direction):
        return Tetromino.ShapeList[self.shapeType]["rotations"][(self.rotation + direction) % 4]
