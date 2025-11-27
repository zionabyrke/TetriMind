import random
import copy
from agent import Agent
from settings import *

class RLGenAlgo:
    def __init__(
        self,
        game_info,
        population_size=20,
        mutation_rate=0.15,
        crossover_rate=0.75,
        elitism=2,
        generations=30,
        depth=1,
    ):
        # the base game info used for simulation
        self.info = game_info

        # GA parameters
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism = elitism
        self.generations = generations

        # search depth for agent chooseAction()
        self.depth = depth

        # ordered list of genetic weight names
        self.weight_keys = [
            "holes", "bumpiness", "maxHeight",
            "line1", "line2", "line3", "line4",
            "tspin1", "tspin2", "tspin3",
            "perfectClear"
        ]

        # create first population of random individuals
        self.population = [
            self.random_weights()
            for _ in range(population_size)
        ]

    # Random weight generator for one individual
    def random_weights(self):
        return {
            # negative fitness impact values
            "holes":        random.uniform(-8, 0),
            "bumpiness":    random.uniform(-4, 0),
            "maxHeight":    random.uniform(-3, 0),

            # line clear positive reward
            "line1":        random.uniform(0, 10),
            "line2":        random.uniform(0, 20),
            "line3":        random.uniform(0, 40),
            "line4":        random.uniform(0, 100),

            # tspin bonuses
            "tspin1":       random.uniform(0, 20),
            "tspin2":       random.uniform(0, 50),
            "tspin3":       random.uniform(0, 100),

            # perfect clear reward
            "perfectClear": random.uniform(0, 1500)
        }

    # Evaluate field with given weight dictionary
    def evaluate_field(self, field, weights):

        # extract board features: holes, bumpiness, heights list
        holes, bumpiness, heights = field.getFieldFeatures()
        maxH = max(heights)

        # compute weighted score
        return (
            # base board structure penalties
            weights["holes"]     * holes +
            weights["bumpiness"] * bumpiness +
            weights["maxHeight"] * maxH +

            # line clear bonuses
            weights["line1"] * (1 if field.lines_cleared == 1 else 0) +
            weights["line2"] * (1 if field.lines_cleared == 2 else 0) +
            weights["line3"] * (1 if field.lines_cleared == 3 else 0) +
            weights["line4"] * (1 if field.lines_cleared == 4 else 0) +

            # tspin bonuses
            weights["tspin1"] * (1 if field.lines_cleared == 1 and field.tspin else 0) +
            weights["tspin2"] * (1 if field.lines_cleared == 2 and field.tspin else 0) +
            weights["tspin3"] * (1 if field.lines_cleared == 3 and field.tspin else 0) +

            # perfect clear check (board fully empty)
            weights["perfectClear"] *
            (1 if all(sum(row)==0 for row in field.blockMatrix) else 0)
        )

    # fitness evaluation for 1 individual weight set
    # plays a small simulated game with max N pieces
    def evaluate_fitness(self, weights, max_pieces=40):
        # deepcopy base info to keep original intact
        temp_info = copy.deepcopy(self.info)

        # agent using cloned game state
        agent = Agent(temp_info)

        # assign evaluation function using these weights
        agent.set_eval_function(lambda f: self.evaluate_field(f, weights))

        score = 0     # cumulative fitness score
        pieces = 0    # how many tetrominos used

        # run small simulated episode
        while pieces < max_pieces:

            # choose the best evaluated move
            _, action = agent.chooseAction(temp_info.field, depth=self.depth)
            if action is None:
                action = (0, 0, 0)  # no rotation, no move, no drop

            rot, dx, drop = action

            # simulate rotation (manual collision)
            if rot == ROTATE_LEFT:
                temp_info.field._rotation_collision(-1)
            elif rot == ROTATE_RIGHT:
                temp_info.field._rotation_collision(1)

            # move piece horizontally preventing collisions
            for _ in range(abs(dx)):
                direction = -1 if dx < 0 else 1
                p = temp_info.field.currentPiece
                new_x = p.coord[0] + direction
                new_y = p.coord[1]
                if not temp_info.field._check_collision(new_x, new_y, p.getShapeArray()):
                    p.coord[0] = new_x

            # simulate full drop (AI pick final landed state)
            agent._simulate_hard_drop(temp_info.field)

            # sum fitness of this new board
            score += self.evaluate_field(temp_info.field, weights)

            pieces += 1

        return score

    # tournament selection of parents
    def tournament_select(self, scores):
        k = 3  # tournament size
        candidate = random.sample(range(self.population_size), k)

        # pick the best score from the sampled candidates
        # USED LAMBDA TO AVOID NESTED FUNCTIONS
        best = max(candidate, key=lambda i: scores[i])
        return self.population[best]

    # swap weights between two parents
    def crossover(self, a, b):
        # random chance to skip crossover entirely
        if random.random() > self.crossover_rate:
            return copy.deepcopy(a), copy.deepcopy(b)

        c1 = {}
        c2 = {}

        # uniform crossover per weight
        for k in self.weight_keys:
            if random.random() < 0.5:
                c1[k], c2[k] = a[k], b[k]
            else:
                c1[k], c2[k] = b[k], a[k]

        return c1, c2

    # mutation (small random changes)
    def mutate(self, indiv):
        for k in self.weight_keys:
            if random.random() < self.mutation_rate:
                indiv[k] += random.uniform(-1, 1)
        return indiv

    # MAIN FLOWWWW
    def run_generation(self): # called by train_screen.py
        # evaluate every individual in current population
        scores = [self.evaluate_fitness(ind) for ind in self.population]

        # sort by descending score
        # USED LAMBDA TO AVOID NESTED FUNCTIONS
        ranked = sorted(zip(scores, self.population), key=lambda x: x[0], reverse=True)

        # elitism: carry over top N directly
        new_pop = [copy.deepcopy(ranked[i][1]) for i in range(self.elitism)]

        # fill remaining population
        while len(new_pop) < self.population_size:
            # pick two parents
            p1 = self.tournament_select(scores)
            p2 = self.tournament_select(scores)

            # generate children
            c1, c2 = self.crossover(p1, p2)

            # mutate children
            self.mutate(c1)
            self.mutate(c2)

            # add to next generation
            new_pop.append(c1)
            if len(new_pop) < self.population_size:
                new_pop.append(c2)

        # update population
        self.population = new_pop

        # return best of this generation
        best_score = ranked[0][0]
        best_weights = ranked[0][1]
        return best_score, best_weights
    
    # final best individual after all generations
    def get_best_final(self):
        scores = [self.evaluate_fitness(ind) for ind in self.population]
        return self.population[scores.index(max(scores))]
