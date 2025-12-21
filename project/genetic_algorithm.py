from agent import Agent
import random
import json
import os
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Agg") # non-GUI

### Set the below constants to preferred files ##

'''BATCH_PATH = "project/data/gene_batch.json"
BEST_PATH = "project/data/best_genome_curr_gen.json"
FITNESS_PLOT = "project/data/fitness_plot.png"
FITNESS_LABEL = "GA Version 1.0 Fitness Curve"'''

BATCH_PATH = "project/data/gene_batch_v2.json"
BEST_PATH = "project/data/best_genome_curr_gen_v2.json"
FITNESS_PLOT = "project/data/fitness_plot_v2.png"
FITNESS_LABEL = "GA Version 2.0 Fitness Curve"

class GeneticAlgorithm(Agent):
    def __init__(self, game, play=False,
            population_size=240,
            mutation_rate=0.05, 
            mutation_step=0.2
    ):
        super().__init__(game)
        self.play = play
        self.model = None
        self.gene_labels = [ # labeling
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
        self.gene_len = len(self.gene_labels)

        if self.play:
            #self.model = list(self.load_best())
            # HANDPICKED MODEL
            # fitness: 3712749
            self.model = [ 
                -0.2638578844150894,
                -0.2153382925237446,
                -0.05462047555844693,
                -0.38913115662719766,
                0.4453283938242215,
                -0.33728202498648757,
                0.1117112800306197,
                -0.4213845809791847,
                -0.19823716448997986,
                -0.2672871544696101,
                -0.1431798397747871,
                -0.13491870660337146
            ]
        else:
            # ga hyperparameters
            self.population_size = population_size
            self.mutation_rate = mutation_rate
            self.mutation_step = mutation_step
            self.population = self.init_population()

            # fitness aligned with population indexes
            self.fitness = [0 for _ in range(self.population_size)]
            self.current_index = 0
            self.generation = 0
            self.fitness_history = []    
            self.game_count = 0
        
    """
        initializes N number of players
        with random weights for every feature key
        inside population
    """
    def init_population(self):
        genomes = []
        for _ in range(self.population_size):
            genes = [(random.random() - 0.5) for _ in range(self.gene_len)]
            genomes.append(genes)
        return genomes # list of lists

    # overwritten method by inheritance:
    def _evaluate_state(self, eval_game):
        value = self.feature_func(eval_game)
        return value

    def choose_action(self, game):
        best_action = None
        best_value = -999999 
        next_states = self.get_next_states(game)

        # evaluate value for the action
        for action in next_states:
            state_eval = self._evaluate_state(next_states[action])
            if state_eval > best_value:
                best_value = state_eval
                best_action = action
        #print(f"{best_action} {state_eval} {best_value}")
        # return converted to action
        return best_action

    def feature_func(self, eval_game):
        features = eval_game.genetics_grid_features()
        w = []
        value = 0.0
        if self.play:
            w = self.model
        else:
            w = self.population[self.current_index]
        
        for i in range(self.gene_len):
            value += w[i] * features[self.gene_labels[i]]
        return value

    # GA methods
    """
    records a genome's fitness (linear reward) for the current genome index
    when all genomes in the population are evaluated, calls evolve()
    """
    def tournament(self, reward):
        top = max(self.fitness)
        self.fitness[self.current_index] = reward
        if reward > top:
            self.save_best()
        self.save_progress()
        self.current_index += 1

        # full generation evaluated?
        if self.current_index >= self.population_size:
            self.evolve()
            self.current_index = 0

    def fitness_logger(self):
        # log generation stats for plotting
        best = max(self.fitness)
        avg = sum(self.fitness) / len(self.fitness)
        self.fitness_history.append((self.generation, best, avg))
        print(f"[GEN {self.generation}] best={best:.2f} avg={avg:.2f}")
        self.plot_fitness()

    """
    samples a parent from top players using:: 
            index = floor((rand^2)*(m-1))
    this favors higher-ranked genomes but keeps randomness
    """
    def random_parent(self, survivors):
        idx = int((random.random() ** 2) * (len(survivors) - 1))
        return survivors[idx]

    """
    Sort genomes by fitness in descending order 
    keep the top 50% as survivors.
    """
    def top_players(self):
        idx = list(range(len(self.population)))
        rank = sorted(idx, key=lambda i: self.fitness[i], reverse=True)
        half = rank[: self.population_size // 2]
        return half
    """
    spawns a baby by per-gene 50/50 inheritance: 
    each gene is copied from mum or dad
    """
    def crossover(self, mum, dad):
        baby = []
        for a, b in zip(mum, dad):
            baby.append(a if random.random() < 0.5 else b)
        return baby

    """
    mutation rate 0.05=5% chance of mutation
    """
    def mutate(self, genome):
        g = genome[:]
        for i in range(self.gene_len):
            if random.random() < self.mutation_rate:
                g[i] += random.uniform(-self.mutation_step, self.mutation_step)
        return g

    """
    Perform the generation update:
      1) top_players (keep top half)
      2) elitism (copy best to next generation)
      3) fill bottom 50% by random_parent, crossover, mutate
      4) # replace population with evolved group
    """
    def evolve(self):
        top = self.top_players()
        new_pop = []

        # elitism
        winner = top[0]
        new_pop.append(self.population[winner][:])#append+copy

        # generate the rest
        while len(new_pop) < self.population_size:
            pa = self.population[self.random_parent(top)]
            pb = self.population[self.random_parent(top)]
            baby = self.crossover(pa, pb)
            baby = self.mutate(baby)
            new_pop.append(baby)

        # logs
        self.fitness_logger()

        # replace
        self.population = new_pop
        self.fitness = [0 for _ in range(self.population_size)]
        self.generation += 1

    """
    makes sure training not be interrupted
    """
    def save_progress(self, path=BATCH_PATH):
        data = {
            "seed": self.game.bag.seed,
            "generation": self.generation,
            "current_index": self.current_index,
            "population_size": self.population_size,
            "population": self.population,
            "fitness": self.fitness,
            "fitness_history": self.fitness_history
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        #print(f"batch saved to {path}")

    def load_progress(self, path=BATCH_PATH):
        if not os.path.exists(path):
            print("no save file")
            return None
        with open(path, "r") as f:
            data = json.load(f)
        self.game.bag.seed = data["seed"]
        self.generation = data["generation"]
        self.current_index = data["current_index"] + 1
        self.population_size = data["population_size"]
        self.population = data["population"]
        self.fitness = data["fitness"]
        self.fitness_history = data["fitness_history"]

        # genome 0 loading: prevent outOfBounds + change seed
        if self.current_index >= self.population_size:
            self.generation += 1
            self.current_index = 0
            self.game.bag.seed = random.randint(0, 2**63-1)
            print(f"new seed: {self.game.bag.seed}")

        print(f"batch loaded from {path}")

    def save_best(self, path=BEST_PATH):
        # index of winner
        winner = max(range(self.population_size), key=lambda i: self.fitness[i])
        data = {
            "generation": self.generation,
            "index": winner,
            "weights": dict(zip(self.gene_labels, self.population[winner])),
            "fitness": self.fitness[winner],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"saved best to {path}")

    def load_best(self, path=BEST_PATH):
        if not os.path.exists(path):
            print("no save file")
            return None
        with open(path, "r") as f:
            data = json.load(f)
        self.generation = data["generation"]
        self.current_index = data["index"]

        return data["weights"].values()

    """
    training metrics
    """
    
    def plot_fitness(self, filename=FITNESS_PLOT):
        if not self.fitness_history:
            print("no fitness history")
            return

        gens = [g for g, _, _ in self.fitness_history]
        best = [b for _, b, _ in self.fitness_history]
        avg  = [a for _, _, a in self.fitness_history]

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(gens, best, label="best")
        ax.plot(gens, avg, label="avg")
        ax.legend()
        ax.grid(True)
        ax.set_title(FITNESS_LABEL)
        ax.set_xlabel("generation")
        ax.set_ylabel("fitness")

        fig.savefig(filename, dpi=150, bbox_inches="tight")
        plt.close(fig)

        print(f"fitness PNG saved to {filename}")
