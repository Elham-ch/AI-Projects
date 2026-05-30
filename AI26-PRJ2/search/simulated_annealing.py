import math
import random

from search.local_search_base import LocalSearchBase


class SimulatedAnnealing(LocalSearchBase):
    def run(self, initial_state, **kwargs):

        max_iterations = kwargs.get("max_iterations", 1500)
        temperature = kwargs.get("initial_temperature", 100.0)
        cooling_rate = kwargs.get("cooling_rate", 0.995)
        min_temperature = kwargs.get("min_temperature", 0.001)

        current_state = [] if not initial_state else list(initial_state)
        if not current_state:
            current_state = self.initialize_state()

        current_cost = self.evaluate(current_state)
        best_state = list(current_state)
        best_cost = current_cost

        evaluations = [current_cost]
        states_history = [list(current_state)]

        for _ in range(max_iterations):
            if temperature <= min_temperature:
                break

            next_state = self.get_neighbor(current_state)
            next_cost = self.evaluate(next_state)

            delta = next_cost - current_cost

            if delta <= 0:
                accept = True
            else:

                accept_probability = math.exp(-delta / temperature)
                accept = random.random() < accept_probability

            if accept:
                current_state = list(next_state)
                current_cost = next_cost

            if current_cost < best_cost:
                best_state = list(current_state)
                best_cost = current_cost

            evaluations.append(current_cost)
            states_history.append(list(current_state))

            temperature *= cooling_rate

        return best_state, best_cost, evaluations, states_history
