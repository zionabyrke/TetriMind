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
        # Check game over
        if self.check_collision(self.currentPiece.coord[0], self.currentPiece.coord[1], self.currentPiece.getShapeArray()):
            print("GAME OVER")
            exit()

    def moveTetromino(self, action, colorMatrix):
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
        # Rotating resets falltimer
        elif action == ROTATE_LEFT:
            self.rotation_collision(-1)
            return
        elif action == ROTATE_RIGHT:
            self.rotation_collision(1)
            return
        elif action == HARD_DROP:
            self.hard_drop(colorMatrix)
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
                self.generateTetromino()
            else:
                self.moveTetromino(MOVE_DOWN, colorMatrix)

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

    # hard drop feature
    def hard_drop(self, colorMatrix):
        x=self.currentPiece.coord[0]
        y=self.currentPiece.coord[1]
        shape_array = self.currentPiece.getShapeArray()
        
        #find col depth until collision
        while not self.check_collision(x, y+1, shape_array):
            y+=1

        #lock piece imeeediately
        self.place_block((x,y), colorMatrix)
        self.currentPiece.coord = [x,y] #update

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
                    [(1,0), (2,0), (0,1), (1,1)],
                    [(0,0), (0,1), (1,1), (1,2)]
                ]
            },
            "Z": {
                "color": RED,
                "rotations": [
                    [(0,0), (1,0), (1,1), (2,1)],
                    [(1,0), (0,1), (1,1), (0,2)]
                ]
            },
            "J": {
                "color": BLUE,
                "rotations": [
                    [(0,0), (0,1), (1,1), (2,1)],
                    [(0,0), (1,0), (0,1), (0,2)],
                    [(0,1), (1,1), (2,1), (2,2)],
                    [(1,0), (1,1), (0,2), (1,2)]
                ]
            },
            "L": {
                "color": ORANGE,
                "rotations": [
                    [(2,0), (0,1), (1,1), (2,1)],
                    [(0,0), (0,1), (0,2), (1,2)],
                    [(0,1), (1,1), (2,1), (0,2)],
                    [(0,0), (1,0), (1,1), (1,2)]
                ]
            },
            "T": {
                "color": PURPLE,
                "rotations": [
                    [(1,0), (0,1), (1,1), (2,1)],
                    [(0,0), (0,1), (1,1), (0,2)],
                    [(0,1), (1,1), (2,1), (1,2)],
                    [(1,0), (0,1), (1,1), (1,2)]
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

    # get rotation info without rotating tetromino
    def getNewOrientation(self, direction):
        n = len(self.ShapeList[self.shapeType]["rotations"])
        return self.ShapeList[self.shapeType]["rotations"][(self.rotation + direction) % n]
