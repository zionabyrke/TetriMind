from game import Game, Gamestate
from settings import *

class Agent:
    def __init__(self, game):
        self.game = game
        self.current_state = None
        self.possible_states = []
        self.piece_per_sec = 1.0 # lower = faster

    def get_game_states(self):
        self.current_state = Gamestate(self.game)
        self.possible_states = [self.current_state]

        # test
        state = self.current_state
        return state.holes, state.bumpiness, state.column_heights

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
                    test = self.test_tspin(this_state)
                    if test:
                        test_piece = test.current_piece
                        test.place_block(test_piece.coord, test_piece.get_shape_array())
                        next_states[(piece.rotation, dx, test.last_action)] = self._evaluate_state(test)
                        ''' sanity checker, habang debug
                        print("Lasst action =", test.last_action, " Rotate Right =", ROTATE_RIGHT, " Left =", ROTATE_LEFT)
                        print((piece.rotation, dx, test.last_action), "Score =", next_states[(piece.rotation, dx, test.last_action)])
                        '''
                    test = None

                #hard dropped
                this_state.place_block((piece.coord[0], piece.coord[1]), shape)
                next_states[(piece.rotation, dx, 0)] = self._evaluate_state(this_state)


        return next_states


    def choose_action(self, game):
        best_action = None
        best_value = (-999999, -999999) # lowest by default
        next_states = self.get_next_states(game)
        # evaluate reward for the action
        for action in next_states:
            # looking for max value (min penalty) out of each state
            if next_states[action] > best_value:
                best_value = next_states[action] #ie:(-1, -1, place_block) left-> rotLeft-> drop
                best_action = action

        # return converted to action
        """
        print("BEST_VALUE", best_value)
        print("BEST_ACTION", best_action)
        """
        return best_action


    def test_tspin(self, game):
        test_left = game.copy()
        test_left.move_tetromino(ROTATE_LEFT, None)
        if test_left.is_tspin():
            return test_left

        test_right = game.copy()
        test_right.move_tetromino(ROTATE_RIGHT, None)
        if test_right.is_tspin():
            return test_right

        return None


    ### Agent helpers (Private methods)
    def _evaluate_state(self, eval_game):
        # rewards
        tspin = eval_game.is_tspin()
        lines_cleared = eval_game.check_line_clears()
        eval_game.update_score(lines_cleared, tspin)

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

  