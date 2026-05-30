import random

from search.local_search_base import LocalSearchBase


class BeamSearch(LocalSearchBase):
    def run(self, initial_state, **kwargs):

        max_iterations = kwargs.get("max_iterations", 60)
        beam_width = max(1, kwargs.get("beam_width", 5))
        neighbor_count = max(1, kwargs.get("neighbor_count", 30))
        random_injections = max(0, kwargs.get("random_injections", 1))
        restart_limit = max(0, kwargs.get("restart_limit", 3))
        stagnation_limit = kwargs.get("stagnation_limit", max(15, max_iterations // 5))
        improvement_epsilon = kwargs.get("improvement_epsilon", 1e-9)
        self._cost_cache = {}

        seed_state = [] if not initial_state else list(initial_state)
        if not seed_state:
            seed_state = self.initialize_state()

        if not self.valid_positions() or self.max_sensors <= 0:
            empty_state = []
            empty_cost = self._cached_evaluate(empty_state)
            return empty_state, empty_cost, [empty_cost], [empty_state]

        beam = self._initial_beam(seed_state, beam_width, neighbor_count)
        scored_beam = self._rank_states(beam)
        best_cost, best_state = scored_beam[0]
        best_state = list(best_state)

        evaluations = [best_cost]
        states_history = [list(best_state)]
        stagnant_iterations = 0
        restarts_used = 0

        for _ in range(max_iterations):
            candidates = []

            for _, state in scored_beam:

                candidates.append(state)
                candidates.extend(
                    self.generate_neighbors(state, max_neighbors=neighbor_count)
                )

            for _ in range(random_injections):
                candidates.append(self._random_state())

            if not candidates:
                break

            scored_beam = self._rank_states(candidates)[:beam_width]
            scored_beam = self._fill_beam(scored_beam, beam_width)
            iteration_cost, iteration_state = scored_beam[0]

            if iteration_cost < best_cost - improvement_epsilon:
                best_state = list(iteration_state)
                best_cost = iteration_cost
                stagnant_iterations = 0
            else:
                stagnant_iterations += 1

            evaluations.append(best_cost)
            states_history.append(list(best_state))

            if stagnant_iterations >= stagnation_limit:
                if restarts_used >= restart_limit:
                    break

                scored_beam = self._rank_states(
                    self._restart_beam(best_state, beam_width)
                )
                stagnant_iterations = 0
                restarts_used += 1

        return best_state, best_cost, evaluations, states_history

    def _cached_evaluate(self, state):
        state = list(state)
        key = tuple(sorted(state))
        if key not in self._cost_cache:
            self._cost_cache[key] = self.evaluate(state)
        return self._cost_cache[key]

    def _rank_states(self, states):
        ranked = []
        seen = set()

        for state in states:
            state = list(state)
            key = tuple(sorted(state))
            if key in seen:
                continue
            seen.add(key)
            ranked.append((self._cached_evaluate(state), state))

        return sorted(ranked, key=lambda item: item[0])

    def _initial_beam(self, seed_state, beam_width, neighbor_count):
        beam = [list(seed_state), self.initialize_state()]
        beam.extend(self.generate_neighbors(seed_state, max_neighbors=neighbor_count))

        attempts = 0
        while len(self._rank_states(beam)) < beam_width and attempts < beam_width * 10:
            beam.append(self._random_state())
            attempts += 1

        return [state for _, state in self._rank_states(beam)[:beam_width]]

    def _restart_beam(self, best_state, beam_width):
        beam = [list(best_state)]


        neighbors = self.generate_neighbors(best_state, max_neighbors=beam_width * 4)
        if neighbors:
            beam.append(self._rank_states(neighbors)[0][1])

        while len(beam) < beam_width:
            beam.append(self._random_state())

        return beam

    def _fill_beam(self, scored_beam, beam_width):
        states = [state for _, state in scored_beam]

        attempts = 0
        while len(states) < beam_width and attempts < beam_width * 10:
            states.append(self._random_state())
            scored_beam = self._rank_states(states)
            states = [state for _, state in scored_beam]
            attempts += 1

        return scored_beam[:beam_width]

    def _random_state(self):
        valid_positions = self.valid_positions()
        max_count = min(self.max_sensors, len(valid_positions))

        if max_count <= 0:
            return []

        if random.random() < 0.75:
            state = self.initialize_state()
            if state:
                return state

        sensor_count = random.randint(1, max_count)
        return random.sample(valid_positions, sensor_count)
