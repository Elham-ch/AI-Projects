import random

from search.local_search_base import LocalSearchBase


class HillClimbing(LocalSearchBase):

    def run(self, initial_state, **kwargs):

        max_iterations = kwargs.get("max_iterations", 500)
        neighbor_count = kwargs.get("neighbor_count", 120)
        max_restarts = kwargs.get("max_restarts", 5)
        sideways_limit = kwargs.get("sideways_limit", 10)
        improvement_epsilon = kwargs.get("improvement_epsilon", 1e-9)

        current_state = [] if not initial_state else list(initial_state)
        if not current_state:
            current_state = self.initialize_state()

        current_cost = self.evaluate(current_state)
        best_state = list(current_state)
        best_cost = current_cost

        evaluations = [current_cost]
        states_history = [list(current_state)]

        restarts_used = 0
        sideways_used = 0

        for _ in range(max_iterations):
            neighbors = self.generate_neighbors(current_state, max_neighbors=neighbor_count)

            if not neighbors:
                break

            neighbor_costs = [(self.evaluate(neighbor), neighbor) for neighbor in neighbors]
            next_cost, next_state = min(neighbor_costs, key=lambda item: item[0])

            improved_current = next_cost < current_cost - improvement_epsilon
            tied_current = abs(next_cost - current_cost) <= improvement_epsilon

            if improved_current:
                current_state = list(next_state)
                current_cost = next_cost
                sideways_used = 0
            elif tied_current and sideways_used < sideways_limit:

                current_state = list(next_state)
                current_cost = next_cost
                sideways_used += 1
            elif restarts_used < max_restarts:

                current_state = self.initialize_state()
                current_cost = self.evaluate(current_state)
                restarts_used += 1
                sideways_used = 0
            else:
                break

            if current_cost < best_cost - improvement_epsilon:
                best_state = list(current_state)
                best_cost = current_cost

            evaluations.append(current_cost)
            states_history.append(list(current_state))

        return best_state, best_cost, evaluations, states_history
