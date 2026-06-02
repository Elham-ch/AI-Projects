import random

from search.local_search_base import LocalSearchBase


class BeamSearch(LocalSearchBase):
    def run(self, initial_state, **kwargs):
        max_iterations = kwargs.get("max_iterations", 100)
        beam_width = max(1, kwargs.get("beam_width", 5))

        beam = self.initial_beam(initial_state, beam_width)
        best_state, best_cost = self.best_state(beam)

        evaluations = [best_cost]
        states_history = [best_state]

        for _ in range(max_iterations):
            successors = []

            for state in beam:
                neighbors = self.generate_neighbors(state)

                if not neighbors:
                    successors.append(state)
                else:
                    successors.extend(neighbors)

            if not successors:
                break

            beam = self.best_states(successors, beam_width)
            current_state, current_cost = self.best_state(beam)

            if current_cost < best_cost:
                best_state = current_state
                best_cost = current_cost

            evaluations.append(current_cost)
            states_history.append(current_state)

            if best_cost == 0:
                break

        return best_state, best_cost, evaluations, states_history

    def initial_beam(self, initial_state, beam_width):
        beam = []

        if initial_state:
            beam.append(initial_state)

        if not self.valid_positions() or self.max_sensors <= 0:
            return beam if beam else [[]]

        attempts = 0

        while len(beam) < beam_width and attempts < beam_width * 10:
            state = self.random_state()

            if not self.seen_before(state, beam):
                beam.append(state)

            attempts += 1

        return beam

    def best_state(self, states):
        scored_states = [(self.evaluate(state), state) for state in states]
        best_cost, best_state = min(scored_states, key=lambda item: item[0])
        return best_state, best_cost

    def best_states(self, states, beam_width):
        unique_states = []

        for state in states:
            if not self.seen_before(state, unique_states):
                unique_states.append(state)

        scored_states = [(self.evaluate(state), state) for state in unique_states]
        scored_states.sort(key=lambda item: item[0])

        return [state for _, state in scored_states[:beam_width]]

    def random_state(self):
        valid_positions = self.valid_positions()
        max_count = min(self.max_sensors, len(valid_positions))

        if max_count <= 0:
            return []

        sensor_count = random.randint(1, max_count)
        return random.sample(valid_positions, sensor_count)

    def seen_before(self, state, states):
        state_key = tuple(sorted(state))
        return any(tuple(sorted(item)) == state_key for item in states)
