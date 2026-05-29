import random

from search.local_search_base import LocalSearchBase


class HillClimbing(LocalSearchBase):

    def run(self, initial_state, **kwargs):
        n_neighbors = kwargs.get("n_neighbors", 40)
        max_iterations = kwargs.get("max_iterations", 600)
        max_sideways = kwargs.get("max_sideways", 25)
        n_restarts = kwargs.get("n_restarts", 6)

        evaluations = []
        states_history = []
        best_state = list(initial_state)
        best_cost = self.evaluate(best_state)

        iters_per_restart = max(1, max_iterations // n_restarts)

        for restart in range(n_restarts):
            if restart == 0:
                current = list(initial_state)
            else:
                current = self.initialize_state()
            current_cost = self.evaluate(current)

            sideways = 0

            for _ in range(iters_per_restart):            
                best_neighbor = None
                best_neighbor_cost = float("inf")
                for _ in range(n_neighbors):
                    neighbor = self.get_neighbor(current)
                    cost = self.evaluate(neighbor)
                    if cost < best_neighbor_cost:
                        best_neighbor_cost = cost
                        best_neighbor = neighbor

                if best_neighbor_cost < current_cost:
                    current, current_cost = best_neighbor, best_neighbor_cost
                    sideways = 0
                elif best_neighbor_cost == current_cost and sideways < max_sideways:
                
                    current = best_neighbor
                    sideways += 1
                else:
                    break

                evaluations.append(current_cost)
                states_history.append(current)

                if current_cost < best_cost:
                    best_cost = current_cost
                    best_state = current

        if not states_history:
            states_history.append(best_state)
            evaluations.append(best_cost)

        return best_state, best_cost, evaluations, states_history
