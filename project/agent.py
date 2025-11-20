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

    def chooseAction(self, field):
        best_action = None
        best_value = -999999 # lowest by default
        piece = field.currentPiece

        # try every rotation actions
        for rot in [ROTATE_LEFT, ROTATE_RIGHT, None]:
            simulate_1 = self._simulate_rotation(field, rot)

            # try from middle spawn to left & rightmost field
            for dx in range(0-(COLUMNS//2), COLUMNS//2): 
                simulate_2 = self._simulate_shift(simulate_1, dx)

                # hard drop to final landing position + line clears
                simu_final = self._simulate_hard_drop(simulate_2)

                # evaluate reward for the action
                value = self._evaluate_state(simu_final)

                # looking for max value (min penalty) out of each state
                if value > best_value:
                    best_value = value #ie:(-1, -1, HARD_DROP) left-> rotLeft-> drop
                    best_action = (rot, dx, HARD_DROP)

        # return converted to action
        return best_action
        #return self._convert_to_action(best_action)

    ### Agent helpers (Private methods)
    def _evaluate_state(self, field):
        holes, bumpiness, heights = field.getFieldFeatures()
        # rewards
        reward = (
            # rewards
            + field.info.playerScore # wala maisip

            # penalties
            -3      * holes          # fewer holes = better
            -1.50   * bumpiness       # smoother surface = better
            -0.25   * max(heights) # avoid tall columns
        )

        return reward

    def _copy_field(self, field):
        _field = Playfield(field.info)

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

    def _convert_to_action(self, best_action):
        if best_action == None: # no move to make
            return HARD_DROP

        rot, dx, drop = best_action
        # if rotation is NOT None = needed
        if rot == ROTATE_LEFT:
            return ROTATE_LEFT
        if rot == ROTATE_RIGHT:
            return ROTATE_RIGHT

        # sideways is NOT None = needed
        if dx < 0:
            return MOVE_LEFT
        if dx > 0:
            return MOVE_RIGHT

        return HARD_DROP 

