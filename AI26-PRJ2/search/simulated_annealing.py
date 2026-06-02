import math
import random

from search.local_search_base import LocalSearchBase


class SimulatedAnnealing(LocalSearchBase):
    def schedule(self, initial_temperature, cooling_rate, t):
        return initial_temperature * math.pow(cooling_rate, t)

    def run(self, initial_state, **kwargs):
        initial_temperature = kwargs.get("initial_temperature", 100.0)
        cooling_rate = kwargs.get("cooling_rate", 0.995)
        min_temperature = kwargs.get("min_temperature", 0.001)

        if not 0 < cooling_rate < 1:
            raise ValueError("cooling_rate must be between 0 and 1")

        current_state = initial_state
        current_cost = self.evaluate(current_state)
        best_state = current_state
        best_cost = current_cost

        evaluations = [current_cost]
        states_history = [current_state]

        t = 0

        while True:
            temperature = self.schedule(initial_temperature, cooling_rate, t)

            if temperature <= min_temperature:
                break

            next_state = self.get_random_neighbor(current_state)
            next_cost = self.evaluate(next_state)

            delta = next_cost - current_cost
            if delta <= 0:
                current_state = next_state
                current_cost = next_cost
            else:
                accept_probability = math.exp(-delta / temperature)
                if random.random() < accept_probability:
                    current_state = next_state
                    current_cost = next_cost

            if current_cost < best_cost:
                best_state = current_state
                best_cost = current_cost

            evaluations.append(current_cost)
            states_history.append(current_state)

            t += 1

        return best_state, best_cost, evaluations, states_history
