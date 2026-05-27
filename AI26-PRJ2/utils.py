import matplotlib.pyplot as plt
import pygame

from env.renderer import Renderer


def draw_results(algorithm_values: list, algorithm_names: list):
    plt.figure(figsize=(10, 5))
    for i in range(algorithm_values.__len__()):
        algorithm_value = algorithm_values[i]
        algorithm_name = algorithm_names[i]
        plt.plot(
            algorithm_value,
            label=algorithm_name
        )

    plt.title("Local Search Algorithms")

    plt.xlabel("Iteration")
    plt.ylabel("Cost")

    plt.legend()

    plt.tight_layout()

    plt.show()


def print_results(algorithm_states: list,
                  algorithm_costs: list,
                  algorithm_names: list):
    for i in range(algorithm_states.__len__()):
        print("\n", algorithm_names[i])
        print("-" * 40)

        print("Final State :", algorithm_states[i])
        print("Final Cost  :", algorithm_costs[i])


def render_history(algorithm_histories: list,
                   algorithm_evaluations: list,
                   algorithm_names: list,
                   world):
    renderer = Renderer(world)

    for i in range(algorithm_histories.__len__()):
        renderer.animate(
            algorithm_histories[i],
            algorithm_evaluations[i],
            algorithm_names[i],
            delay=1000,
        )

    pygame.quit()


def represent(best_states: list, best_costs: list,
              evaluations: list, histories: list,
              names: list, world):
    print_results(algorithm_states=best_states,
                  algorithm_costs=best_costs,
                  algorithm_names=names)

    draw_results(algorithm_values=evaluations,
                 algorithm_names=names)

    # for visualisation purposes only. you can comment this part.
    render_history(algorithm_histories=histories,
                   algorithm_evaluations=evaluations,
                   algorithm_names=names,
                   world=world)
