from game import GameInfo, Playfield, Tetromino, GameState
from settings import *

class Agent:
    def __init__(self, info):
        self.info = info
        self.field = self.info.field #blockMatrix inside
        self.currentState = None
        self.possibleStates = []
        self.piecePerSec = 1.0/self.field.fallSpeed
    
    def getGameState(self):
        self.currentState = GameState(self.info)
        self.possibleStates = [self.currentState]

        # test
        state = self.currentState
        return state.holes, state.bumpiness, state.columnHeights

    def get_next_states(self, field):
        field_copy = self._copy_field(field)
        piece = field_copy.currentPiece
        next_states = {}

        if piece.shapeType == "O":
            rotations = 1
        elif piece.shapeType == "I" or piece.shapeType == "S" or piece.shapeType == "Z":
            rotations = 2
        else:
            rotations = 4

        # try every rotation actions
        for rot in range(rotations):
            piece.rotate(1)
            shape = piece.getShapeArray()
            leftmost_x = min(shape, key = lambda coords:coords[0])[0]
            rightmost_x = max(shape, key = lambda coords:coords[0])[0]

            # try from middle spawn to left & rightmost field
            for dx in range(0-leftmost_x, COLUMNS-rightmost_x): 
                # hard drop to final landing position + line clears
                piece.coord[0], piece.coord[1] = field_copy._depth_collide(dx, 0)

                # add action state pair
                # actions are of the form (initial rotation, distance from spawn x coordinate, rotation at the bottom for t spin)
                this_state = self._copy_field(field_copy)

                # try t spin rotates
                if piece.shapeType == "T":
                    test = self.test_tspin(this_state)
                    if test:
                        test_piece = test.currentPiece
                        test._place_block(test_piece.coord, test_piece.getShapeArray())
                        next_states[(piece.rotation, dx, test.last_action)] = self._evaluate_state(test)
                        ''' sanity checker, habang debug
                        print("Lasst action =", test.last_action, " Rotate Right =", ROTATE_RIGHT, " Left =", ROTATE_LEFT)
                        print((piece.rotation, dx, test.last_action), "Score =", next_states[(piece.rotation, dx, test.last_action)])
                        '''
                    test = None

                #hard dropped
                this_state._place_block((piece.coord[0], piece.coord[1]), shape)
                next_states[(piece.rotation, dx, 0)] = self._evaluate_state(this_state)


        return next_states


    def chooseAction(self, field):
        best_action = None
        best_value = (-999999, -999999) # lowest by default
        next_states = self.get_next_states(field)
        # evaluate reward for the action
        for action in next_states:
            # looking for max value (min penalty) out of each state
            if next_states[action] > best_value:
                best_value = next_states[action] #ie:(-1, -1, HARD_DROP) left-> rotLeft-> drop
                best_action = action

        # return converted to action
        '''
        print("BEST_VALUE", best_value)
        print("BEST_ACTION", best_action)
        '''
        return best_action


    def test_tspin(self, field):
        test_left = self._copy_field(field)
        test_left.moveTetromino(ROTATE_LEFT, None)
        if test_left.is_tspin():
            return test_left

        test_right = self._copy_field(field)
        test_right.moveTetromino(ROTATE_RIGHT, None)
        if test_right.is_tspin():
            return test_right

        return None

    ### Agent helpers (Private methods)
    def _evaluate_state(self, eval_field):
        # rewards
        tspin = eval_field.is_tspin()
        lines_cleared = eval_field._check_line_clears()
        eval_field.info._updateScore(lines_cleared, tspin)

        holes, bumpiness, heights = eval_field.getFieldFeatures()

        reward = (
            # rewards
            eval_field.info.playerScore, # wala maisip

            # penalties
            -3      * holes          # fewer holes = better
            -1.50   * bumpiness       # smoother surface = better
            -0.25   * max(heights) # avoid tall columns
        )

        return reward

    def _copy_field(self, field):
        # gameinfo laso needs to be copied omg
        _info = GameInfo()
        _info.playerScore = field.info.playerScore
        _field = Playfield(_info)

        # duplicate currentPiece as cp
        cp = field.currentPiece
        _field.currentPiece = Tetromino(cp.shapeType)
        _field.currentPiece.coord = cp.coord[:]
        _field.currentPiece.rotation = cp.rotation

        # duplicate nextPiece as np
        np = field.nextPiece
        _field.nextPiece = Tetromino(np.shapeType)
        _field.nextPiece.coord = np.coord[:]
        _field.nextPiece.rotation = np.rotation

        _field.blockMatrix = [row[:] for row in field.blockMatrix]
        
        return _field

    def _simulate_rotation(self, field, rot):
        if rot is None: # no rotation is needed
            return field

        _field = self._copy_field(field)
        _orientation = 0

        if rot == ROTATE_LEFT:
            _orientation = -1
        else:
            _orientation = 1
        
        # check collision
        _field._rotation_collision(_orientation)

        return _field

    def _simulate_shift(self, field, dx):
        if dx == 0: # no sideways needed
            return field

        _field = self._copy_field(field)
        piece = _field.currentPiece
        num_steps = abs(dx) # relative to COLUMN//2 leftmost (-)
        direction = 0

        if dx < 0: # left of mid spawn
            direction = -1 # moveLeft
        else:
            direction = 1 #moveRight

        for _ in range(num_steps):
            new_x = piece.coord[0] + direction
            new_y = piece.coord[1]

            # check collision
            if not _field._check_collision(new_x, new_y, piece.getShapeArray()):
                piece.coord[0] = new_x
            else:
                break # corner

        return _field

    # hard drop + line clearing
    def _simulate_hard_drop(self, field):
        _field = self._copy_field(field)
        piece = _field.currentPiece
        x, y = piece.coord
        shape = piece.getShapeArray()

        # for line clears simulation
        new_matrix = []
        cleared = 0

        # check collision (ground)
        while not _field._check_collision(x, y+1, shape):
            y+=1
        piece.coord[1] = y

        # lock piece
        for dx, dy in shape:
            _field.blockMatrix[y + dy][x + dx] = 1

        for row in _field.blockMatrix: #line clearing top-bottom
            if all(row):
                cleared += 1
            else:
                new_matrix.append(row)

        # add rows on top
        for _ in range(cleared):
            new_matrix.insert(0, [0] * len(_field.blockMatrix[0]))
        _field.blockMatrix = new_matrix

        return _field

