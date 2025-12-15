## TetriMind
A Tetris Game with Reinforcement Learning AI Agent

# Setup
- Clone the repository and install dependencies from `requirements.txt`

      pip install -r requirements.txt

- Open the folder in Visual Studio Code and run:

      python3 project/main.py

<br>

# Features
- Classic Tetris with responsive controls
- Player vs AI mode with difficulty levels
- Realistic AI moves
- Versus AI garbage lines
- T-spins
- Retrainable Tetris Agent (Genetic Algorithm)

## Results
# Genetic Algorithm
- Generations: 25
- Population: 60
- Mutation rate: 0.05
- Mutation step: 0.2
- Reward/Fitness: pieces survived + lines cleared
- Feature function: holes, bumpiness, weighted height, cumulative height, relative height, vertical hole tunnels, max well depth, sum wells, weighted filled cells, landing height, hole depth, row hole
- Games: 1,500 full

![Genetic Algorithm Fitness Curve](fitness_plot.png)

# Tech Stack
Language: Python
<br>Main Library: pygame
<br>Dev Library: pyinstaller (exe bundling), matplotlib (training)

## Useful Links:
- [Reinforcement Learning on Tetris](https://rex-l.medium.com/reinforcement-learning-on-tetris-707f75716c37)
- [Evolving Tetris AI based on genetic algorithms](https://github.com/mzmousa/tetris-ai?tab=readme-ov-file)