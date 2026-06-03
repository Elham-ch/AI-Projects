import math
import random

from search.local_search_base import LocalSearchBase


class SimulatedAnnealing(LocalSearchBase):
    def schedule(self, initial_temperature, cooling_rate, t):
        return initial_temperature * math.pow(cooling_rate, t)

    def run(self, initial_state, **kwargs):
        max_iterations = kwargs.get("max_iterations", 1000)
        initial_temperature = kwargs.get("initial_temperature", 100.0)
        cooling_rate = kwargs.get("cooling_rate", 0.995)
        min_temperature = kwargs.get("min_temperature", 0.001)

        current_state = initial_state
        current_cost = self.evaluate(current_state)
        best_state = current_state
        best_cost = current_cost

        evaluations = [current_cost]
        states_history = [current_state]

        for t in range(max_iterations):
            temperature = self.schedule(initial_temperature, cooling_rate, t)

            if temperature <= min_temperature:
                break

            next_state = self.get_random_neighbor(current_state)
            next_cost = self.evaluate(next_state)

            delta = current_cost - next_cost
            if delta > 0:
                current_state = next_state
                current_cost = next_cost
            else:
                accept_probability = math.exp(delta / temperature)
                if random.random() < accept_probability:
                    current_state = next_state
                    current_cost = next_cost

            if current_cost < best_cost:
                best_state = current_state
                best_cost = current_cost

            evaluations.append(current_cost)
            states_history.append(current_state)

        return best_state, best_cost, evaluations, states_history
