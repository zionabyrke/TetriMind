from settings import *
import random
import datetime

LINE_SCORES = {0:0, 1: 100, 2: 300, 3: 500, 4: 800}
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

class GameInfo:
    def __init__(self):
        self.playerScore = 0
        self.gameLevel = 1
        self.elapsedTime = 0

    def updateGameInfo(self, dt):
        self.elapsedTime += dt

    def _updateScore(self, lines_cleared, is_tspin):
        if is_tspin:
            self.playerScore += T_SPIN.get(lines_cleared, 0)
        else:
            self.playerScore += LINE_SCORES.get(lines_cleared, 0)

class Tetromino:
    def __init__(self, shape):
        self.coord = [(COLUMNS//2)-2, 0]
        self.rotation = 0 # index 0 orig orientation 
        self.shapeType = shape
        self.color = ShapeList[self.shapeType]["color"]

    # returns the shape array
    def getShapeArray(self):
        return ShapeList[self.shapeType]["rotations"][self.rotation]

    # changes orientation in circular manner
    def rotate(self, direction):
        self.rotation = (self.rotation + direction) % 4

    # get rotation info without rotating tetromino
    def getNewOrientation(self, direction):
        return ShapeList[self.shapeType]["rotations"][(self.rotation + direction) % 4]


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

        # flags & counters
        self.lines_cleared = 0
        self.lines_cleared_so_far = 0
        self.landing_height = 0
        self.tspins = 0
        self.tetris = 0
        self.last_action = None
        self.game_over = False

    def generateTetromino(self):
        if not self.bag:
            self.bag = list(ShapeList.keys())
            random.shuffle(self.bag)
        self.currentPiece = self.nextPiece
        self.nextPiece = Tetromino(self.bag.pop())
        # Check game over
        if self._check_collision(self.currentPiece.coord[0], self.currentPiece.coord[1], self.currentPiece.getShapeArray()):
            self.game_over = True

    def moveTetromino(self, action, colorMatrix):
        piece = self.currentPiece
        if not piece: #if no piece falling
            return
        self.last_action = action

        if action == HARD_DROP:
            return self._hard_drop(colorMatrix)
        # Rotating resets falltimer
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
            self.fallTimer = 0

        ## CHECK BOUNDS COLLISION 
        if not self._check_collision(piece.coord[0] + dx, piece.coord[1] + dy, piece.getShapeArray()):
            piece.coord[0] += dx
            piece.coord[1] += dy


    # handles falling and checking for block placement (called by main)
    def update(self, dt, colorMatrix): 
        self.fallTimer += dt 
        if self.fallTimer >= self.fallSpeed * 1000: 
            self.fallTimer = 0 
            _coords = self.currentPiece.coord

            # Check if we will place block by checking collisions from coords (x,y+1)
            if self._check_collision(_coords[0], _coords[1]+1, self.current_piece.get_shape_array()):
                self.place_block(_coords, self.current_piece.get_shape_array(), color_matrix)
                self.lines_cleared = self.check_line_clears(color_matrix)
                self.lines_cleared_so_far += self.lines_cleared
                self.generate_tetromino()
            else:
                self.moveTetromino(MOVE_DOWN, colorMatrix)
        
    def ghost_piece(self):
        x,y = self.currentPiece.coord
        shape_array = self.currentPiece.getShapeArray()
        x,y = self._depth_collide(x,y)

        self.landing_height = y

        # adjust y coord[1] as ghost piece
        ghost = [] #temp coord list
        for dx, dy in shape_array:
            ghost.append((x+dx, y+dy))

        return ghost #display on main
    
    def getFieldFeatures(self): #called by agent {Public}
        _holes = 0
        _bumpiness = 0
        _columnHeights = [0] * COLUMNS

        # colHeights find first occupied cell
        for col in range(COLUMNS):
            col_height = 0
            for row in range(ROWS):
                if self.blockMatrix[row][col] != 0:
                    # first filled row from top found = rows - row_index
                    col_height = ROWS - row
                    break
            _columnHeights[col] = col_height

        # holes each cols that have 1 block & under it is 0
        for col in range(COLUMNS):
            # count holes under the first filled block (1)
            block_found = False
            for row in range(ROWS):
                if self.blockMatrix[row][col] != 0:
                    block_found = True
                elif block_found:
                    _holes += 1

        for col in range(COLUMNS - 1):
            # since neighbor col can be higher
            _bumpiness += abs(_columnHeights[col] - _columnHeights[col + 1])

        return _holes, _bumpiness, _columnHeights

    # for genetic algorithm use
    def genetics_grid_features(self):
        holes = 0
        bumpiness = 0
        cumulative_height = 0
        weighted_height = 0
        relative_height = 0
        vertical_hole_clusters = 0
        max_well_depth = 0
        sum_wells = 0
        weighted_filled_cells = 0
        hole_depth = 0
        row_hole = 0

        column_heights = [0] * COLUMNS
        holes_per_col = [0] * COLUMNS
        row_has_hole = [0] * ROWS

        for col in range(COLUMNS):
            first_block_row = None
            current_holes = 0
            hole_depth_accum = 0

            # cluster = 1 continuous vertical holes in a column
            # True = found
            cluster_active = False

            for row in range(ROWS):
                cell = self.block_matrix[row][col]
                # if block found first time => record height
                if cell == 1:
                    weighted_filled_cells += (ROWS - row)

                    if first_block_row is None:
                        first_block_row = row

                    # close cluster ONLY if hole-cluster is below stack base
                    if cluster_active and row > first_block_row:
                        vertical_hole_clusters += 1
                        cluster_active = False

                else: # only count holes BELOW first block
                    if first_block_row is not None:
                        current_holes += 1
                        row_has_hole[row] = 1
                        hole_depth_accum += (ROWS - first_block_row)

                        if not cluster_active:
                            cluster_active = True
            # end of column, close cluster if open
            if cluster_active:
                vertical_hole_clusters += 1

            # results
            column_heights[col] = 0 if first_block_row is None else (ROWS - first_block_row)
            holes_per_col[col] = current_holes
            holes += current_holes
            hole_depth += hole_depth_accum

        # heights
        max_h = max(column_heights)
        min_h = min(column_heights)
        relative_height = max_h - min_h
        cumulative_height = sum(column_heights)
        weighted_height = sum(h*h for h in column_heights)

        # bumpiness
        for c in range(COLUMNS - 1):
            bumpiness += abs(column_heights[c] - column_heights[c+1])
        # wells
        for c in range(COLUMNS):
            left = column_heights[c-1] if c > 0 else 99
            right = column_heights[c+1] if c < COLUMNS - 1 else 99
            w = max(0, min(left, right) - column_heights[c])
            sum_wells += w
            max_well_depth = max(max_well_depth, w)

        row_hole = sum(row_has_hole)

        return {
            "holes": holes,
            "bumpiness": bumpiness,
            "lines_cleared": self.lines_cleared,
            "weighted_height": weighted_height,
            "cumulative_height": cumulative_height,
            "relative_height": relative_height,
            "vertical_hole_clusters": vertical_hole_clusters,
            "max_well_depth": max_well_depth,
            "sum_wells": sum_wells,
            "weighted_filled_cells": weighted_filled_cells,
            "landing_height": self.landing_height,
            "hole_depth": hole_depth,
            "row_hole": row_hole
        }

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

        return True

    #### PRIVATE PLAYFIELD HELPER METHODS ####
    # Returns true if a boundary or block collision was dected, false otherwise
    def _check_collision(self, new_x, new_y, shape_array):
        for dx, dy in shape_array:
            dx+=new_x
            dy+=new_y

            if dx < 0 or dx >= COLUMNS or dy < 0 or dy >= ROWS or self.blockMatrix[dy][dx] > 0:
                return True
        return False

    # checks for collisions whrn rotating, adjusts coordinates to fit rotation
    # based on super roation system of modern tetris games
    def _rotation_collision(self, direction):
        piece = self.currentPiece
        
        new_rotation = (piece.rotation+direction)%4
        test_coords = []
        if piece.shapeType == "O":
            return
        elif piece.shapeType == "I":
            test_coords = I_wall_kick_dict.get((piece.rotation, new_rotation))
        else:   #wall kicks for all other pieces
            test_coords = wall_kick_dict.get((piece.rotation, new_rotation))

        # test for valid coordinates derived using wall kick dict and rotate if a test is passed
        rotation_image = piece.getNewOrientation(direction)
        curr_x, curr_y = piece.coord
        for dx, dy in test_coords:
            if not self._check_collision(curr_x+dx, curr_y+dy, rotation_image):
                piece.coord[0] = curr_x+dx
                piece.coord[1] = curr_y+dy
                piece.rotate(direction)
                self.fallTimer = 0
                return

    # places the blocks of current tetromino on block matrix and the color matrix
    def _place_block(self, coords, colorMatrix):
        for x, y in self.currentPiece.getShapeArray():
            self.blockMatrix[coords[1] + y][coords[0] + x] = 1
            colorMatrix[coords[1] + y][coords[0] + x] = self.currentPiece.color

    # Called every time board gets updated
    def _check_line_clears(self, colorMatrix):
        # Check for any completed line from the y pos of current piece up to y+4
        line_clears = 0
        for y in range(self.currentPiece.coord[1], self.currentPiece.coord[1]+4):
            if y >= ROWS:
                break
            if all(self.blockMatrix[y]):
                self.blockMatrix.pop(y)
                colorMatrix.pop(y)
                self.blockMatrix.insert(0, [0 for _ in range(COLUMNS)])
                colorMatrix.insert(0, [BLACK for _ in range(COLUMNS)])
                line_clears+=1

        return line_clears

    def _hard_drop(self, colorMatrix):
        x,y = self.currentPiece.coord
        x,y = self._depth_collide(x,y)

        #lock piece imeeediately
        self._place_block((x,y), colorMatrix)
        self.currentPiece.coord = [x,y] #update
        self.fallTimer = self.fallSpeed*1000

    def _depth_collide(self, x, y):
        _shape_array=self.currentPiece.getShapeArray()
            
        #find col depth until collision
        while not self._check_collision(x, y+1, _shape_array):
            y+=1

        return x,y

    def update_score(self, lines_cleared, is_tspin):
        if is_tspin:
            self.tspins += 1
            self.player_score += T_SPIN.get(lines_cleared, 0)
        else:
            if lines_cleared == 4:
                self.tetris += 1
            self.player_score += LINE_SCORES.get(lines_cleared, 0)

    # extracts the game state from Game
    def copy(self):
        _game = Game(self.bag.copy())
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

    def reset(self, seed):
        self.__init__(self.bag)
        self.bag.reset(seed)

# to add:
# save_game()
# load_game()
# update the game level
