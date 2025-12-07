from agent import Agent
import random
import copy
import json
import os
import matplotlib
import matplotlib.pyplot as plt
"""
    Genome means player
    Gene means set of weights
    population size min 60, avg 80, >120 max potential
"""

class GeneticAlgorithm(Agent):
    def __init__(self, game, reset=True, 
            population_size=3, # test
            mutation_rate=0.05, 
            mutation_step=0.2
    ):
        super().__init__(game)
        # reset, superclass Agent() can be used by others
        self.move_time=0
        self.action_sequence=0
        self.action=None

        # ga hyperparameters
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_step = mutation_step

        self.genes = [ # labeling
            "holes",
            "bumpiness",
            "lines_cleared",
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
        self.genomes = []
        self.babies = []
        self.current_genome_index = 0
        self.generation = 0
        self.fitness_history = []

        # reset = saved best genomes will be overwritten
        self.reset = reset
        if reset or not self.load_best(): # unsuccessful
            self.init_population()
        """else:
            if not self.load_best(): # unsuccessful
                self.init_population()"""


    # overwritten method by inheritance:
    def _evaluate_state(self, eval_game):
        tspin = eval_game.is_tspin()
        lines_cleared = eval_game.check_line_clears()
        eval_game.update_score(lines_cleared, tspin)

        value = self.value_actions(eval_game)
        return value

    def choose_action(self, game):
        best_action = None
        best_value = -999999 
        next_states = self.get_next_states(game)

        # evaluate value for the action
        for action in next_states:
            # looking for max value (min penalty) out of each state
            state_eval = self._evaluate_state(next_states[action])
            if state_eval > best_value:
                best_value = state_eval
                best_action = action
        print(f"{best_action} {state_eval} {best_value}")
        # return converted to action
        return best_action

    # GA methods
    """
    initializes N genomes with random weights for every feature key
    genome's fitness=0
    """
    def init_population(self): 
        self.genomes = []
        for _ in range(self.population_size):
            # form: dictionary
            genome = {k: (random.random() - 0.5) for k in self.genes}
            # no holes on fresh board
            genome["holes"] = random.random() * 0.5
            genome["vertical_hole_clusters"] = random.random() * 0.5
            genome["hole_depth"] = random.random() * 0.5
            genome["row_hole"] = random.random() * 0.5
            # no lines cleared yet
            genome["line_cleared"] = 0
            # add genome info
            genome["id"] = int(random.random()*10000000)
            genome["fitness"] = 0
            self.genomes.append(genome)

    # for actual game
    def eval_game(self):
        features = self.game.genetics_grid_features()
        genome = self.genomes[self.current_genome_index]
        reward = 0
        for k in self.genes:
            # dot product of weights and features
            reward += genome[k] * features[k]
        return reward

    """
    same as eval_game but accepts a simulated game so the agent
    can evaluate hypothetical placements without altering real game
    """
    def value_actions(self, sim_game):
        features = sim_game.genetics_grid_features()
        genome = self.genomes[self.current_genome_index]
        reward = 0
        for k in self.genes:
            reward += genome[k] * features[k]
        return reward

    """
    records a genome's fitness (episode score) for the current genome index
    when all genomes in the population are evaluated, calls evolve()
    """
    def tournament(self, value):
        self.genomes[self.current_genome_index]["fitness"] = value
        self.current_genome_index += 1
        if self.current_genome_index >= len(self.genomes):
            self.evolve()
            self.current_genome_index = 0

        #self.save_best() # saving best genome happens

    """
    samples a parent from top players using:: 
            index = floor((rand^2)*(m-1))
    this favors higher-ranked genomes but keeps randomness
    """
    def random_parent(self):
        max_index = len(self.genomes) - 1
        current_genome_indexx = int((random.random() ** 2) * max_index)
        return self.genomes[current_genome_indexx]

    """
    Sort genomes by fitness in descending order 
    keep the top 50% as survivors.
    """
    def top_players(self):
        self.genomes.sort(key=lambda g: g["fitness"], reverse=True)
        self.genomes = self.genomes[:self.population_size // 2]
    """
    spawns a baby by per-gene 50/50 inheritance: 
    each gene is copied from mum or dad
    """
    def crossover(self, mum, dad):
        baby = {}
        for k in self.genes:
            baby[k] = mum[k] if random.random() < 0.5 else dad[k]
        return baby

    """
    mutation rate 0.05=5% chance of mutation
    """
    def mutate(self, genome):
        for k in self.genes:
            if random.random() < self.mutation_rate:
                # cc: https://github.com/mzmousa/tetris-ai?tab=readme-ov-file
                genome[k] += random.random() * self.mutation_step * 2 - self.mutation_step
        return genome

    """
    Perform the generation update:
      1) top_players (keep top half)
      2) elitism (copy best to next generation)
      3) fill bottom 50% by random_parent, crossover, mutate
      4) # replace population with evolved group
    """
    def evolve(self):
        self.generation += 1
        self.top_players()
        new_population = []
        best = copy.deepcopy(self.genomes[0])
        new_population.append(best)
        #print("EVOLVE CALLED")

        #self.fitness_log()

        while len(new_population) < self.population_size:
            p1 = self.random_parent()
            p2 = self.random_parent()
            baby = self.crossover(p1, p2)
            baby = self.mutate(baby)
            baby["fitness"] = 0
            new_population.append(baby)

        self.genomes = new_population

    # tests
    def get_current_weights(self):
        return self.genomes[self.current_genome_index]

    def fitness_log(self):
        best = self.genomes[0]["fitness"]
        avg = sum(g["fitness"] for g in self.genomes) / len(self.genomes)
        self.fitness_history.append((self.generation, best, avg))
        print(f"[GEN {self.generation}] best={best:.2f} avg={avg:.2f}")


    """
    makes sure training not be interrupted
    """
    def save_best(self, path="best_genome_v0.json"):
        best = self.genomes[0]
        data = {"generation": self.generation,
                "weights": {k: best[k] for k in self.genes},
                "id": best["id"],
                "fitness": best["fitness"]}
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        #print(f"saved best to {path}")
    
    def load_best(self, path="best_genome_v0.json"):
        if not os.path.exists(path):
            print("no save file")
            return False
        with open(path, "r") as f:
            data = json.load(f)
        if len(self.genomes) == 0: # at least 1 genome
            self.genomes.append({k: 0 for k in self.genes})
        for k in self.genes:
            self.genomes[0][k] = data["weights"][k]
        self.genomes[0]["id"] = data["id"]
        self.genomes[0]["fitness"] = 0
        self.generation = data["generation"]
        #print(f"loaded best from {path}")
        return True
    
    
    """
    training metrics
    """

    
    def plot_fitness(self, filename="fitness_plot.png"):
        matplotlib.use("Agg")   # non-GUI

        if not self.fitness_history:
            print("no fitness history")
            return

        gens = [g for g, _, _ in self.fitness_history]
        best = [b for _, b, _ in self.fitness_history]
        avg  = [a for _, _, a in self.fitness_history]

        fig, ax = plt.subplots(figsize=(10, 5))  # create figure (required to save PNG)

        ax.plot(gens, best, label="best")
        ax.plot(gens, avg, label="avg")
        ax.legend()
        ax.grid(True)
        ax.set_title("GA Fitness Curve")
        ax.set_xlabel("generation")
        ax.set_ylabel("fitness")

        fig.savefig(filename, dpi=150, bbox_inches="tight")
        plt.close(fig)

        print(f"fitness PNG saved to {filename}")

  

