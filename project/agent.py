from game import *
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

    def chooseAction(self, field, depth=1):
        best_action = None
        best_value = -999999 # lowest by default

        # base case for recursion:
        if depth <= 0:
            return self._evaluate_state(field), None
        

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

                # recursion for nextPiece
                # simulate next piece spawn
                next_field = self._copy_env(simu_final)
                next_field.currentPiece = Tetromino(next_field.nextPiece.shapeType)
                next_field.currentPiece.coord = next_field.nextPiece.coord[:]
                next_field.currentPiece.rotation = next_field.nextPiece.rotation

                # randomize next-next piece (your game already does this)
                next_field.bag = list(ShapeList.keys())
                random.shuffle(next_field.bag)

                # recursion
                next_value, _ = self.chooseAction(next_field, depth - 1)
                total_value = value + next_value

                # looking for max value (min penalty) out of each state
                if total_value > best_value:
                    best_value = total_value #ie:(-1, -1, HARD_DROP) left-> rotLeft-> drop
                    best_action = (rot, dx, HARD_DROP)

        # return converted to action
        return best_value, best_action

    ### Agent helpers (Private methods)
    def _evaluate_state(self, field):
        holes, bumpiness, heights = field.getFieldFeatures()
        # --- PERFECT CLEAR BONUS ---
        perfect_clear_bonus = 1000 if all(sum(row) == 0 for row in field.blockMatrix) else 0
        # rewards
        reward = (
            # rewards
            + LINE_SCORES.get(field.lines_cleared, 0)
            + T_SPIN.get(field.lines_cleared, 0)
            + perfect_clear_bonus

            # penalties
            -3      * holes          # fewer holes = better
            -1.50   * bumpiness       # smoother surface = better
            -0.25   * max(heights) # avoid tall columns
        )

        return reward

    def _copy_env(self, field):
        env = Playfield(field.info)

        # duplicate currentPiece as cp
        cp = field.currentPiece
        env.currentPiece = Tetromino(cp.shapeType)
        env.currentPiece.coord = cp.coord[:]
        env.currentPiece.rotation = cp.rotation

        # duplicate nextPiece as np
        np = field.nextPiece
        env.nextPiece = Tetromino(np.shapeType)
        env.nextPiece.coord = np.coord[:]
        env.nextPiece.rotation = np.rotation

        env.blockMatrix = [row[:] for row in field.blockMatrix]
        
        return env

    def _simulate_rotation(self, field, rot):
        if rot is None: # no rotation is needed
            return field

        _field = self._copy_env(field)
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

        _field = self._copy_env(field)
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
        _field = self._copy_env(field)
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

