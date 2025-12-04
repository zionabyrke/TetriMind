from settings import *
import random
import datetime

#seed that starts with Z->T
#random.seed(1)
#random.seed(5)
#random.seed(20)
random.seed(30)
BAG = []

LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}
T_SPIN = {1:800, 2: 1200, 3: 1600}
BLOCKFALL_RATE = 36 # Blocks fall every 36 frames
#shapeList disctionary
ShapeList = {
    "S": {"color": GREEN, "rotations": [
            [(1,0), (2,0), (0,1), (1,1)],
            [(1,0), (1,1), (2,1), (2,2)],
            [(1,1), (2,1), (0,2), (1,2)],
            [(0,0), (0,1), (1,1), (1,2)]]
    },
    "Z": {"color": RED, "rotations": [
            [(0,0), (1,0), (1,1), (2,1)],
            [(2,0), (1,1), (2,1), (1,2)],
            [(0,1), (1,1), (1,2), (2,2)],
            [(1,0), (0,1), (1,1), (0,2)]]
    },
    "J": {"color": BLUE, "rotations": [
            [(0,0), (0,1), (1,1), (2,1)],
            [(1,0), (2,0), (1,1), (1,2)],
            [(0,1), (1,1), (2,1), (2,2)],
            [(1,0), (1,1), (0,2), (1,2)]]
    },
    "L": {"color": ORANGE, "rotations": [
            [(2,0), (0,1), (1,1), (2,1)],
            [(1,0), (1,1), (1,2), (2,2)],
            [(0,1), (1,1), (2,1), (0,2)],
            [(0,0), (1,0), (1,1), (1,2)]]
    },
    "T": {"color": PURPLE, "rotations": [
            [(1,0), (0,1), (1,1), (2,1)],
            [(1,0), (1,1), (2,1), (1,2)],
            [(0,1), (1,1), (2,1), (1,2)],
            [(1,0), (0,1), (1,1), (1,2)]]
    },
    "O": {"color": YELLOW, "rotations": [
            [(1,0), (2,0), (1,1), (2,1)],
            [(1,0), (2,0), (1,1), (2,1)],
            [(1,0), (2,0), (1,1), (2,1)],
            [(1,0), (2,0), (1,1), (2,1)]]
    },
    "I": {"color": CYAN, "rotations": [
            [(0,1), (1,1), (2,1), (3,1)],
            [(2,0), (2,1), (2,2), (2,3)],
            [(0,2), (1,2), (2,2), (3,2)],
            [(1,0), (1,1), (1,2), (1,3)]]
    }
}
# List of wall kick test types
type_1 = [(0,0), (-1, 0), (-1,-1), (0, 2), (-1, 2)]
type_2 = [(0,0), (1, 0), (1,1), (0, -2), (1, -2)]
type_3 = [(0,0), (1, 0), (1,-1), (0, 2), (1, 2)]
type_4 = [(0,0), (-1, 0), (-1,1), (0, -2), (-1, -2)]

# keys from dict are formed with the tuple: (current_rotation, new_rotation)
# the table for the rotations can be seen from https://tetris.wiki/Super_Rotation_System#Wall_Kicks
wall_kick_dict = {(0, 1): type_1, (1, 0): type_2, (1, 2): type_2, (2, 1): type_1,
    (2, 3): type_3, (3, 2): type_4, (3, 0): type_4, (0, 3): type_3}

# Wall kick test types and dict but for the I piece
I_type_1 = [(0,0), (-2,0), (1,0), (-2,1), (1,-2)]
I_type_2 = [(0,0), (2,0), (-1,0), (2,-1), (1,2)]
I_type_3 = [(0,0), (-1,0), (2,0), (-1,-2), (2,1)]
I_type_4 = [(0,0), (1,0), (-2,0), (1,2), (-2, -1)]

I_wall_kick_dict = {(0, 1): I_type_1, (1, 0): I_type_2, (1, 2): I_type_3, (2, 1): I_type_4,
    (2, 3): I_type_2, (3, 2): I_type_1, (3, 0): I_type_4, (0, 3): I_type_3}


# usage: only 1 bag for both human and agent
# maintains a 7Bag for fastest player
# the slowest player can access the up-popped bag
# since fastest player do not pop them
class Bag:
    # no pop() since it causes Multiplayer unsynch
    # used pointer instead
    def __init__(self, start_pointer=0):
        self.pointer = start_pointer

        # adjust 7 to 14 if Agent needs deeper search
        self._add(self.pointer + 7)

    #Extend the global 7-bag until long enough
    def _add(self, need_size):
        global BAG
        while len(BAG) < need_size:
            bag = list(ShapeList.keys())
            random.shuffle(bag) # shuffles before extend
            BAG.extend(bag)

    # grab a piece from global bag and advance player pointer
    def pull(self):
        global BAG
        self._add(self.pointer + 1)
        shape = BAG[self.pointer]
        self.pointer += 1

        return Tetromino(shape)

    #grab future piece without advancing pointer
    def peek(self, index=0):
        pos = self.pointer + index
        self._add(pos + 1)
        return Tetromino(BAG[pos])

    def copy(self):
        return Bag(start_pointer=self.pointer)

    def reset(self):
        BAG.clear()
        self.pointer = 0
        # adjust 7 to 14 if Agent needs deeper search
        self._add(7)


class Gamestate:
    def __init__(self, game):
        self.game = game
        self.current_piece = self.game.current_piece
        self.next_piece = self.game.next_piece
        self.score = self.game.player_score 

        _holes, _bumpiness, _column_heights = self.game.get_field_features()
        self.holes = _holes
        self.bumpiness = _bumpiness
        self.column_heights = _column_heights

        """
        # new add extraction to get_field_features()
        self.pileHeight = 0
        self.connectedHoles = 0
        self.removedRows = 0
        self.maxWellDepth = 0
        self.rowTransitions = 0
        self.colTransitions = 0
        self.landingHeight = 0
        self.wellSum = 0
        self.altitude = 0
        self.filledCells = 0
        """

    # get_field_features()
    def set_game_states(self, game):
        # add extractions of remaining game states
        self.__init__(game) # reset class

        # colHeights find first occupied cell
        for col in range(COLUMNS):
            for row in range(ROWS):
                if self.block_matrix[row][col] != 0:
                    # first filled row from top found = rows - row_index
                    self.column_heights[col] = ROWS - row
                    break

         # holes each cols that have 1 block & under it is 0
        for c in range(COLUMNS):
            # count holes under the first filled block (1)
            block_found = False
            for r in range(ROWS):
                if self.block_matrix[r][c]:
                    block_found = True
                elif block_found:
                    self.holes += 1

        self.bumpiness = sum(abs(self.heights[i] - self.heights[i + 1])
                        for i in range(COLUMNS - 1))


class Tetromino:
    def __init__(self, shape_type):
        self.coord = [(COLUMNS//2)-2, 0]
        self.rotation = 0 # index 0 orig orientation 
        self.shape_type = shape_type
        self.color = ShapeList[self.shape_type]["color"]

    # copies the shape
    def copy(self):
        return Tetromino(self.shape_type)

    # returns the shape array
    def get_shape_array(self):
        return ShapeList[self.shape_type]["rotations"][self.rotation]

    # changes orientation in circular manner
    def rotate(self, direction):
        self.rotation = (self.rotation + direction) % 4

    # get rotation info without rotating tetromino
    def get_new_orientation(self, direction):
        return ShapeList[self.shape_type]["rotations"][(self.rotation + direction) % 4]


class Game:
    def __init__(self, bag):
        self.bag = bag
        self.block_matrix = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_piece = self.bag.pull()
        self.next_piece = self.bag.pull()
        self.fall_speed = BLOCKFALL_RATE / FRAMEPERSEC
        self.fall_timer = 0

        #game info
        self.player_score = 0
        self.game_level = 1
        self.elapsed_time = 0

        # flags
        self.lines_cleared = 0
        self.lines_cleared_so_far = 0
        self.last_action = None
        self.game_over = False

    def generate_tetromino(self):
        self.current_piece = self.next_piece
        self.next_piece = self.bag.pull()
        
        # collision on spawn = game over
        if self._check_collision(self.current_piece.coord[0],
                                 self.current_piece.coord[1],
                                 self.current_piece.get_shape_array()):
            self.game_over = True

    def move_tetromino(self, action, color_matrix):
        piece = self.current_piece
        if not piece: #if no piece falling
            return
        self.last_action = action

        if action == HARD_DROP:
            return self._hard_drop(color_matrix)
        # Rotating resets fall_timer
        if action == ROTATE_LEFT:
            self._rotation_collision(-1)
            return
        elif action == ROTATE_RIGHT:
            self._rotation_collision(1)
            return

        dx, dy = 0, 0
        if action == MOVE_LEFT:
            dx = -1
        elif action == MOVE_RIGHT:
            dx = 1
        elif action == MOVE_DOWN:
            dy = 1
            self.fall_timer = 0

        ## CHECK BOUNDS COLLISION 
        if not self._check_collision(piece.coord[0] + dx, piece.coord[1] + dy, piece.get_shape_array()):
            piece.coord[0] += dx
            piece.coord[1] += dy


    # handles falling and checking for block placement (called by main)
    def update(self, dt, color_matrix): 
        self.fall_timer += dt 
        if self.fall_timer >= self.fall_speed * 1000: 
            self.fall_timer = 0 
            _coords = self.current_piece.coord

            # Check if we will place block by checking collisions from coords (x,y+1)
            if self._check_collision(_coords[0], _coords[1]+1, self.current_piece.get_shape_array()):
                self.place_block(_coords, self.current_piece.get_shape_array(), color_matrix)
                tspin = self.is_tspin()
                lines_cleared = self.check_line_clears(color_matrix)
                self.lines_cleared_so_far += lines_cleared
                self.update_score(lines_cleared, tspin)
                self.generate_tetromino()
            else:
                self.move_tetromino(MOVE_DOWN, color_matrix)
        
    def ghost_piece(self):
        x,y = self.current_piece.coord
        shape_array = self.current_piece.get_shape_array()
        x,y = self.depth_collide(x,y)

        # adjust y coord[1] as ghost piece
        ghostPiece = [] #temp coord list
        for dx, dy in shape_array:
            ghostPiece.append((x+dx, y+dy))

        return ghostPiece #display on main
    
    def get_field_features(self): #called by agent {Public}
        _holes = 0
        _bumpiness = 0
        _column_heights = [0] * COLUMNS

        # colHeights find first occupied cell
        for col in range(COLUMNS):
            col_height = 0
            for row in range(ROWS):
                if self.block_matrix[row][col] != 0:
                    # first filled row from top found = rows - row_index
                    col_height = ROWS - row
                    break
            _column_heights[col] = col_height

        # holes each cols that have 1 block & under it is 0
        for col in range(COLUMNS):
            # count holes under the first filled block (1)
            block_found = False
            for row in range(ROWS):
                if self.block_matrix[row][col] != 0:
                    block_found = True
                elif block_found:
                    _holes += 1

        for col in range(COLUMNS - 1):
            # since neighbor col can be higher
            _bumpiness += abs(_column_heights[col] - _column_heights[col + 1])

        return _holes, _bumpiness, _column_heights

    def is_tspin(self):
        if not(self.last_action == ROTATE_RIGHT or self.last_action == ROTATE_LEFT) or self.current_piece.shape_type != "T":
            return False
        x, y = self.current_piece.coord[0], self.current_piece.coord[1]
        shape = self.current_piece.get_shape_array()
        #check piece mobility to the left, right and up
        #if it can move there then it's not a t-spin
        if not (self._check_collision(x+1, y, shape) and 
            self._check_collision(x-1, y, shape) and 
            self._check_collision(x, y-1, shape)):
            return False
        print("reached here")

        return True

    #### PRIVATE PLAYFIELD HELPER METHODS ####
    # Returns true if a boundary or block collision was dected, false otherwise
    def _check_collision(self, new_x, new_y, shape_array):
        for dx, dy in shape_array:
            dx+=new_x
            dy+=new_y

            if dx < 0 or dx >= COLUMNS or dy < 0 or dy >= ROWS or self.block_matrix[dy][dx] > 0:
                return True
        return False

    # checks for collisions whrn rotating, adjusts coordinates to fit rotation
    # based on super roation system of modern tetris games
    def _rotation_collision(self, direction):
        piece = self.current_piece
        
        new_rotation = (piece.rotation+direction)%4
        test_coords = []
        if piece.shape_type == "O":
            return
        elif piece.shape_type == "I":
            test_coords = I_wall_kick_dict.get((piece.rotation, new_rotation))
        else:   #wall kicks for all other pieces
            test_coords = wall_kick_dict.get((piece.rotation, new_rotation))

        # test for valid coordinates derived using wall kick dict and rotate if a test is passed
        rotation_image = piece.get_new_orientation(direction)
        curr_x, curr_y = piece.coord
        for dx, dy in test_coords:
            if not self._check_collision(curr_x+dx, curr_y+dy, rotation_image):
                piece.coord[0] = curr_x+dx
                piece.coord[1] = curr_y+dy
                piece.rotate(direction)
                self.fall_timer = 0
                return

    # places the blocks of current tetromino on block matrix and the color matrix
    def place_block(self, coords, shape, color_matrix=None):
        for x, y in self.current_piece.get_shape_array():
            self.block_matrix[coords[1] + y][coords[0] + x] = 1
            if color_matrix:
                color_matrix[coords[1] + y][coords[0] + x] = self.current_piece.color

    # Called every time board gets updated
    def check_line_clears(self, color_matrix=None):
        # Check for any completed line from the y pos of current piece up to y+4
        line_clears = 0
        for y in range(self.current_piece.coord[1], self.current_piece.coord[1]+4):
            if y >= ROWS:
                break
            if all(self.block_matrix[y]):
                self.block_matrix.pop(y)
                self.block_matrix.insert(0, [0 for _ in range(COLUMNS)])
                if color_matrix:
                    color_matrix.pop(y)
                    color_matrix.insert(0, [BLACK for _ in range(COLUMNS)])
                line_clears+=1

        return line_clears

    def _hard_drop(self, color_matrix):
        x,y = self.current_piece.coord
        x,y = self.depth_collide(x,y)

        #lock piece imeeediately
        self.place_block((x,y), self.current_piece.get_shape_array(), color_matrix)
        self.current_piece.coord = [x,y] #update
        self.fall_timer = self.fall_speed*1000

    def soft_drop(self):
        self.current_piece.coord[0], self.current_piece.coord[1] = self.depth_collide(self.current_piece.coord[0], self.current_piece.coord[1])

    def depth_collide(self, x, y):
        _shape_array=self.current_piece.get_shape_array()
            
        #find col depth until collision
        while not self._check_collision(x, y+1, _shape_array):
            y+=1

        return x,y

    def update_score(self, lines_cleared, is_tspin):
        if is_tspin:
            self.player_score += T_SPIN.get(lines_cleared, 0)
        else:
            self.player_score += LINE_SCORES.get(lines_cleared, 0)

    # extracts the game state from Game
    def copy(self):
        # gamegame laso needs to be copied omg
        _game = Game(self.bag)
        _game.player_score = self.player_score

        # duplicate current_piece as cp
        cp = self.current_piece
        _game.current_piece = cp.copy()
        _game.current_piece.coord = cp.coord[:]
        _game.current_piece.rotation = cp.rotation

        # duplicate next_piece as np
        np = self.next_piece
        _game.next_piece = cp.copy()
        _game.next_piece.coord = np.coord[:]
        _game.next_piece.rotation = np.rotation

        _game.block_matrix = [row[:] for row in self.block_matrix]
        
        return _game

    def reset(self):
        self.__init__(self.bag)

# to add:
# save_game()
# load_game()
# update the game level
