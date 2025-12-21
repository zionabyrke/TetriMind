from agent import Agent
import random
from collections import deque
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers

class DQNAgent(Agent):
    ## The neural estimates the VALUE of a resulting board state
    # the network approximates V(s) (the expected return of a given state)

    def __init__(
        self,
        game,
        gamma=0.99,                  # future reward discount factor
        epsilon=1.0,                 # initial exploration probability
        epsilon_min=0.05,            # minimum exploration probability
        epsilon_decay=0.995,         # exploration decay rate
        replay_size=50000,           # max experiences to store
        batch_size=64,               # learning minibatch sizes
        learning_rate=0.001,         # optimizer learning rate
        target_sync_interval=1000    # steps of copying weights to target network
    ):
        super().__init__(game)

        # RL hyperparameters
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_sync_interval = target_sync_interval

        # exploration parameters of epsilon-greedy policy
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # replay memory stores past experiences (s', r, done)
        self.replay_buffer = deque(maxlen=replay_size)

        # counter of learning steps to sync target network
        self.learn_step = 0

        # fixed order keys
        self.feature_keys = [
            "holes",
            "bumpiness",
            "weighted_height",
            "cumulative_height",
            "relative_height",
            "vertical_hole_clusters",
            "max_well_depth",
            "sum_wells",
            "weighted_filled_cells",
            "landing_height",
            "hole_depth",
            "row_hole"
        ]
        self.keys_len = len(self.feature_keys)

        # build networks
        # model: main network for prediction and training
        # target_model: provides delayed targets for main network
        self.model = self._build_network(learning_rate)
        self.target_model = self._build_network(learning_rate)
        self._sync_target_network() # initialize target network weights

        

    # overridden
    def choose_action(self, game):
        ## epsilon greedy policy inside
        next_states = self.get_next_states(game)
        actions = list(next_states.keys())

        if not actions:
            return None

        # epsilon-greedy
        if random.random() < self.epsilon:
            # explore
            return random.choice(actions)

        # exploit: argmax V(s')
        # for each action, evaluate the resulting board state
        best_action = max(actions,
            key=lambda a: self._predict_value(next_states[a])
        )

        return best_action

    def store_transition(self, next_state, reward, done):
        """
        Stores (s', r, done) in replay memory
        does not store (s, a) explicitly
        because learning happens on s' next state
        """
        self.replay_buffer.append((next_state, reward, done))


    def learn(self):
        """
        Performs one learning step tru experience replay
        1. samples a random minibatch from replay memory
        2. for each next_state in batch:
           - If terminal, target = reward
           - Else target = reward + gamma * max(V(s'')) for next-next states
        3. converts batch to arrays and trains the network
        4. decays epsilon to reduce exploration over time
        5. syncs target network every target_sync_interval steps
        """
        if len(self.replay_buffer) < self.batch_size:
            return # not enough data to learn

        batch = random.sample(self.replay_buffer, self.batch_size)

        states = []
        targets = []

        for next_state, reward, done in batch:
            # convert state features to numeric array
            state_features = self._features_to_array(next_state)

            if done:
                # If terminal, the value is the immediate reward
                target_value = reward
            else:
                next_next_states = self.get_next_states(next_state)
                if not next_next_states:
                    target_value = reward
                else:
                    # limit number of next-next states
                    # JUST A TESTING FOR THE BUG!!!
                    sample_states = list(next_next_states.values())[:10]
                    max_future = max(
                        self._predict_target_value(s) for s in sample_states
                    )
                    target_value = reward + self.gamma * max_future

            states.append(state_features)
            targets.append(target_value)

        # convert to arrays
        states = np.array(states, dtype=np.float32)
        targets = np.array(targets, dtype=np.float32)

        # train model on the batch using Mean Squared Error
        self.model.train_on_batch(states, targets)

        # for logging tracking learning progress
        self.learn_step += 1
        self._decay_epsilon() # gradually reduce exploration

        # intervally copy weights to target network
        if self.learn_step % self.target_sync_interval == 0:
            self._sync_target_network()


    """
        PRIVATE METHODS
                        """

    def _build_network(self, learning_rate):
        """
        simple fully connected neural network
        Input size = number of features (state dimension)
        Output size = 1 (V(s))
        """
        model = models.Sequential([
            layers.Input(shape=(self.keys_len,)),
            layers.Dense(128, activation="relu"),
            layers.Dense(128, activation="relu"),
            layers.Dense(1, activation="linear")
        ])

        model.compile(
            optimizer=optimizers.Adam(learning_rate=learning_rate),
            loss="mse" # changeable loss function
        )

        return model


    def _features_to_array(self, game):
        features_dict = game.genetics_grid_features()
    
        # convert to array in fixed order
        features_array = np.array([features_dict[k] for k in self.feature_keys], dtype=np.float32)
        return features_array


    def _predictor(self, game):
        features = np.array(
            self._features_to_array(game),
            dtype=np.float32
        )
        features = np.expand_dims(features, axis=0)
        return features

    def _predict_value(self, game):
        # Returns predicted value V(s) using main network
        # for exploitation (choose_action)
        features = self._predictor(game)
        return self.model.predict(features, verbose=0)[0, 0]


    def _predict_target_value(self, game):
        # returns V(s) using target network
        features = self._predictor(game)
        return self.target_model.predict(features, verbose=0)[0, 0]


    def _sync_target_network(self):
        # copies weights from training network to target network
        self.target_model.set_weights(
            self.model.get_weights()
        )


    def _decay_epsilon(self):
        # reduces exploration rate over times
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay
        )
