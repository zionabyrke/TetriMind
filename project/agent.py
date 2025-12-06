from game import Game
from settings import *

class Agent:
    def __init__(self, game):
        self.game = game
        # move per sec is based on 60 frame per sec
        self.move_per_sec = 2/60 # lower = faster

    def get_game_states(self):
        return game.get_field_features()

    def get_next_states(self, game):
        game_copy = game.copy()
        piece = game_copy.current_piece
        next_states = {}

        if piece.shape_type == "O":
            rotations = 1
        elif piece.shape_type == "I" or piece.shape_type == "S" or piece.shape_type == "Z":
            rotations = 2
        else:
            rotations = 4

        # try every rotation actions
        for rot in range(rotations):
            piece.rotate(1)
            shape = piece.get_shape_array()
            leftmost_x = min(shape, key = lambda coords:coords[0])[0]
            rightmost_x = max(shape, key = lambda coords:coords[0])[0]

            # try from middle spawn to left & rightmost game
            for dx in range(0-leftmost_x, COLUMNS-rightmost_x): 
                # hard drop to final landing position + line clears
                piece.coord[0], piece.coord[1] = game_copy.depth_collide(dx, 0)

                # add action state pair
                # actions are of the form (initial rotation, distance from spawn x coordinate, rotation at the bottom for t spin)
                this_state = game_copy.copy()

                # try t spin rotates
                if piece.shape_type == "T":
                    test_left = self.test_tspin(this_state, ROTATE_LEFT)
                    if test_left:
                        test_left.place_block(test_left.current_piece.coord, test_left.current_piece.get_shape_array())
                        next_states[(piece.rotation, dx, ROTATE_LEFT)] = test_left

                    test_right = self.test_tspin(this_state, ROTATE_RIGHT)
                    if test_right:
                        test_right.place_block(test_right.current_piece.coord, test_right.current_piece.get_shape_array())
                        next_states[(piece.rotation, dx, ROTATE_RIGHT)] = test_right

                #hard dropped
                this_state.place_block((piece.coord[0], piece.coord[1]), shape)
                next_states[(piece.rotation, dx, 0)] = this_state


        return next_states


    def choose_action(self, game):
        best_action = None
        best_value = (-999999, -999999) # lowest by default
        next_states = self.get_next_states(game)

        # evaluate reward for the action
        for action in next_states:
            # looking for max value (min penalty) out of each state
            state_eval = self._evaluate_state(next_states[action])
            if state_eval > best_value:
                best_value = state_eval
                best_action = action

        # return converted to action
        return best_action


    def test_tspin(self, game, direction):
        test = game.copy()
        test.move_tetromino(direction, None)
        if test.is_tspin():
            return test
        return None


    ### Agent helpers (Private methods)
    def _evaluate_state(self, eval_game):
        # rewards
        lines_cleared = eval_game.check_line_clears()

        holes, bumpiness, heights = eval_game.get_field_features()

        reward = (
            # rewards
            eval_game.player_score, # wala maisip

            # penalties
            -3      * holes          # fewer holes = better
            -1.50   * bumpiness       # smoother surface = better
            -0.25   * max(heights) # avoid tall columns
        )

        return reward

  