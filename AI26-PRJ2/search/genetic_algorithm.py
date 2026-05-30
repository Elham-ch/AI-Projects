import random

from search.local_search_base import LocalSearchBase


class GeneticAlgorithm(LocalSearchBase):
    def run(self, initial_state, **kwargs):

        generations = kwargs.get("generations", kwargs.get("max_iterations", 60))
        population_size = max(2, kwargs.get("population_size", 24))
        elite_size = kwargs.get("elite_size", max(2, population_size // 10))
        elite_size = min(max(1, elite_size), population_size - 1)
        tournament_size = max(2, kwargs.get("tournament_size", 4))
        crossover_rate = kwargs.get("crossover_rate", 0.85)
        mutation_rate = kwargs.get("mutation_rate", 0.25)
        repair_rate = kwargs.get("repair_rate", 0.3)
        repair_scan_limit = kwargs.get("repair_scan_limit", 8)
        immigrant_rate = kwargs.get("immigrant_rate", 0.15)
        stagnation_limit = kwargs.get("stagnation_limit", max(20, generations // 3))
        improvement_epsilon = kwargs.get("improvement_epsilon", 1e-9)
        self._cost_cache = {}

        seed_state = self._copy_individual(initial_state)
        if not seed_state:
            seed_state = self.initialize_state()

        if not self.valid_positions() or self.max_sensors <= 0:
            empty_state = []
            empty_cost = self._cached_evaluate(empty_state)
            return empty_state, empty_cost, [empty_cost], [empty_state]

        population = self._initial_population(seed_state, population_size)
        scored_population = self._score_population(population)

        best_cost, best_state = scored_population[0]
        best_state = list(best_state)
        evaluations = [best_cost]
        states_history = [list(best_state)]
        stagnant_generations = 0

        for _ in range(generations):
            next_population = [
                list(individual)
                for _, individual in scored_population[:elite_size]
            ]

            immigrant_count = int(population_size * immigrant_rate)
            for _ in range(immigrant_count):
                if len(next_population) >= population_size:
                    break
                next_population.append(self._random_individual())

            while len(next_population) < population_size:
                parent_a = self._select_parent(scored_population, tournament_size)
                parent_b = self._select_parent(scored_population, tournament_size)

                child = self._crossover(parent_a, parent_b, crossover_rate)
                child = self._mutate(child, mutation_rate)
                if random.random() < repair_rate:
                    child = self._repair(child, repair_scan_limit)
                next_population.append(child)

            population = self._deduplicate_population(next_population, population_size)
            scored_population = self._score_population(population)
            generation_cost, generation_best = scored_population[0]

            if generation_cost < best_cost - improvement_epsilon:
                best_state = list(generation_best)
                best_cost = generation_cost
                stagnant_generations = 0
            else:
                stagnant_generations += 1

            evaluations.append(best_cost)
            states_history.append(list(best_state))

            if stagnant_generations >= stagnation_limit:
                population = self._restart_population(best_state, population_size)
                scored_population = self._score_population(population)
                stagnant_generations = 0

        return best_state, best_cost, evaluations, states_history

    def _score_population(self, population):
        return sorted(
            (self._cached_evaluate(individual), self._copy_individual(individual))
            for individual in population
        )

    def _cached_evaluate(self, individual):
        individual = self._copy_individual(individual)
        key = tuple(individual)
        if key not in self._cost_cache:
            self._cost_cache[key] = self.evaluate(individual)
        return self._cost_cache[key]

    def _copy_individual(self, individual):
        if not individual:
            return []
        return list(individual)[: self.max_sensors]

    def _initial_population(self, seed_state, population_size):
        population = []
        seen = set()

        def add_individual(candidate):
            candidate = self._copy_individual(candidate)
            key = tuple(sorted(candidate))
            if key not in seen:
                seen.add(key)
                population.append(candidate)

        add_individual(seed_state)
        add_individual(self.initialize_state())

        for neighbor in self.generate_neighbors(seed_state, max_neighbors=population_size * 2):
            add_individual(neighbor)
            if len(population) >= population_size:
                return population

        attempts = 0
        while len(population) < population_size and attempts < population_size * 10:
            add_individual(self._random_individual())
            attempts += 1

        while len(population) < population_size:
            population.append(list(random.choice(population)))

        return population

    def _restart_population(self, best_state, population_size):
        population = [self._copy_individual(best_state)]
        while len(population) < population_size:
            population.append(self._random_individual())
        return population

    def _random_individual(self):
        valid_positions = self.valid_positions()
        max_count = min(self.max_sensors, len(valid_positions))

        if max_count <= 0:
            return []


        if random.random() < 0.7:
            individual = self.initialize_state()
            if individual:
                return individual

        sensor_count = random.randint(1, max_count)
        return random.sample(valid_positions, sensor_count)

    def _select_parent(self, scored_population, tournament_size):
        sample_size = min(tournament_size, len(scored_population))
        contenders = random.sample(scored_population, sample_size)
        return list(min(contenders, key=lambda item: item[0])[1])

    def _crossover(self, parent_a, parent_b, crossover_rate):
        parent_a = self._copy_individual(parent_a)
        parent_b = self._copy_individual(parent_b)

        if random.random() > crossover_rate:
            return list(random.choice([parent_a, parent_b]))

        genes = []
        for sensor in parent_a:
            if random.random() < 0.5:
                genes.append(sensor)
        for sensor in parent_b:
            if random.random() < 0.5:
                genes.append(sensor)

        if not genes:
            combined = parent_a + parent_b
            if combined:
                genes.append(random.choice(combined))

        return self._copy_individual(genes)

    def _mutate(self, individual, mutation_rate):
        mutant = self._copy_individual(individual)
        if random.random() >= mutation_rate:
            return mutant

        operations = [
            self._move_sensor,
            self._add_sensor,
            self._remove_sensor,
            self._reposition_sensor,
            self._two_sensor_reassignment,
        ]

        mutation_steps = 2 if random.random() < 0.2 else 1
        for _ in range(mutation_steps):
            mutant = random.choice(operations)(mutant)

        return self._copy_individual(mutant)

    def _repair(self, individual, scan_limit=8):
        individual = self._copy_individual(individual)
        individual = self._drop_redundant_sensor(individual, scan_limit)
        individual = self._add_useful_sensor(individual, scan_limit)
        return self._copy_individual(individual)

    def _drop_redundant_sensor(self, individual, scan_limit):
        current = self._copy_individual(individual)
        current_cost = self._cached_evaluate(current)

        sensors = list(current)
        random.shuffle(sensors)

        best_candidate = current
        best_cost = current_cost

        for sensor in sensors[:scan_limit]:
            candidate = [position for position in current if position != sensor]
            candidate_cost = self._cached_evaluate(candidate)
            if candidate_cost < best_cost:
                best_candidate = candidate
                best_cost = candidate_cost

        return self._copy_individual(best_candidate)

    def _add_useful_sensor(self, individual, scan_limit):
        current = self._copy_individual(individual)
        current_cost = self._cached_evaluate(current)

        if len(current) >= self.max_sensors:
            return current

        positions = [
            position
            for position in self._candidate_positions_for_add(current)
            if position not in current
        ]

        if not positions:
            return current

        best_position = None
        best_cost = current_cost


        for position in positions[:scan_limit]:
            candidate = current + [position]
            candidate_cost = self._cached_evaluate(candidate)
            if candidate_cost < best_cost:
                best_position = position
                best_cost = candidate_cost

        if best_position is None:
            return current

        return self._copy_individual(current + [best_position])

    def _add_sensor(self, individual):
        current = self._copy_individual(individual)
        if len(current) >= self.max_sensors:
            return current

        candidates = [
            position
            for position in self._candidate_positions_for_add(current)
            if position not in current
        ]

        if not candidates:
            candidates = [
                position
                for position in self.valid_positions()
                if position not in current
            ]

        if candidates:
            current.append(random.choice(candidates))

        return self._copy_individual(current)

    def _remove_sensor(self, individual):
        current = self._copy_individual(individual)
        if not current:
            return current

        sensor = random.choice(current)
        return [position for position in current if position != sensor]

    def _move_sensor(self, individual):
        current = self._copy_individual(individual)
        if not current:
            return self._add_sensor(current)

        occupied = set(current)
        index = random.randrange(len(current))
        sensor = current[index]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_position = (sensor[0] + dx, sensor[1] + dy)
            if new_position not in occupied and self.position_valid(*new_position):
                current[index] = new_position
                break

        return self._copy_individual(current)

    def _reposition_sensor(self, individual):
        current = self._copy_individual(individual)
        if not current:
            return self._add_sensor(current)

        occupied = set(current)
        candidates = [
            position
            for position in self._candidate_positions_for_add(current)
            if position not in occupied
        ]

        if not candidates:
            candidates = [
                position
                for position in self.valid_positions()
                if position not in occupied
            ]

        if candidates:
            current[random.randrange(len(current))] = random.choice(candidates)

        return self._copy_individual(current)

    def _two_sensor_reassignment(self, individual):
        current = self._copy_individual(individual)
        if len(current) < 2:
            return self._reposition_sensor(current)

        occupied = set(current)
        candidates = [
            position
            for position in self._candidate_positions_for_add(current)
            if position not in occupied
        ]

        if len(candidates) < 2:
            candidates = [
                position
                for position in self.valid_positions()
                if position not in occupied
            ]

        if len(candidates) >= 2:
            first_index, second_index = random.sample(range(len(current)), 2)
            first_position, second_position = random.sample(candidates, 2)
            current[first_index] = first_position
            current[second_index] = second_position

        return self._copy_individual(current)

    def _deduplicate_population(self, population, population_size):
        unique_population = []
        seen = set()

        for individual in population:
            individual = self._copy_individual(individual)
            key = tuple(sorted(individual))
            if key not in seen:
                seen.add(key)
                unique_population.append(individual)

            if len(unique_population) >= population_size:
                return unique_population

        while len(unique_population) < population_size:
            unique_population.append(self._random_individual())

        return unique_population
