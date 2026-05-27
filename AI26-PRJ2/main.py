"""
University: University of Isfahan
Faculty: Mathematics and Statistics
Branch: Computer Science
Course: Artificial Intelligence
Professor: Dr. Faria Nasiri Mofakham
TAs: MehrAzin Marzough, Mohammad Karimi, Anahita Honarmandian
Project: Implementing Local Search Algorithms for a Sensor Placement Optimization Problem
"""
from env.grid_world import GridWorld
from search.hill_climbing import HillClimbing
from search.simulated_annealing import SimulatedAnnealing
from utils import represent

import re
import matplotlib
matplotlib.use("TkAgg")


def run_algorithms(world, initial_state, algorithm_classes):
    best_states = []
    best_costs = []
    evaluations = []
    histories = []
    names = []

    for algorithm_class in algorithm_classes:
        # Format class name for presentation (e.g., HillClimbing -> Hill Climbing)
        name = re.sub(r'(?<!^)([A-Z])', r' \1', algorithm_class.__name__)
        names.append(name)
        
        # Instantiate the algorithm
        algorithm_instance = algorithm_class(world)
        
        print(f"\nRunning {name}...")
        
        # TODO: Execute the algorithm by calling its run method.
        # Make sure your run methods accept the initial_state and return the 4 required outputs:
        # best_state, best_cost, evaluations, states_history
        state, cost, evals, hist = algorithm_instance.run(initial_state)
        
        best_states.append(state)
        best_costs.append(cost)
        evaluations.append(evals)
        histories.append(hist)

    # Display terminal results, performance plots, and pygame animation
    represent(
        best_states=best_states,
        best_costs=best_costs,
        evaluations=evaluations,
        histories=histories,
        names=names,
        world=world
    )


if __name__ == "__main__":
    
    # Load the grid world map configuration (e.g., "map1")
    world = GridWorld("map1")

    # TODO: Add your bonus algorithm classes to this list (e.g., GeneticAlgorithm, BeamSearch, TabuSearch)
    algorithm_classes = [
        HillClimbing,
        SimulatedAnnealing
    ]

    # TODO: Initialize and assign the starting state for the experiments.
    # Note: For a fair comparison, all algorithms must start from the exact same initial configuration.
    # Hint: You can use the initialize_state() method implemented in your search classes.
    initial_state = ...

    # Run the evaluation pipeline
    run_algorithms(world, initial_state, algorithm_classes)