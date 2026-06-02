import random

from search.local_search_base import LocalSearchBase


class GeneticAlgorithm(LocalSearchBase):
    def run(self, initial_state, **kwargs):
        generations = kwargs.get("generations", kwargs.get("max_iterations", 500))
        population_size = max(2, kwargs.get("population_size", 30))
        mutation_rate = kwargs.get("mutation_rate", 0.1)
        fit_enough = kwargs.get("fit_enough", 0)

        current_state = initial_state

        population = self.initial_population(current_state, population_size)
        current_state, current_cost = self.best_individual(population)
        best_state, best_cost = current_state, current_cost

        evaluations = [best_cost]
        states_history = [best_state]

        for _ in range(generations):
            weights = self.weighted_by(population)
            population2 = []

            for _ in range(len(population)):
                parent1, parent2 = random.choices(
                    population,
                    weights=weights,
                    k=2
                )

                child = self.reproduce(parent1, parent2)

                if random.random() < mutation_rate:
                    child = self.mutate(child)

                population2.append(child)

            population = population2
            current_state, current_cost = self.best_individual(population)

            if current_cost < best_cost:
                best_state = current_state
                best_cost = current_cost

            evaluations.append(best_cost)
            states_history.append(best_state)

            if best_cost <= fit_enough:
                break

        return best_state, best_cost, evaluations, states_history

    def weighted_by(self, population):
        return [self.fitness(individual) for individual in population]

    def fitness(self, individual):
        return 1 / (1 + self.evaluate(individual))

    def best_individual(self, population):
        scored_population = [
            (self.evaluate(individual), individual) for individual in population
        ]
        best_cost, best_state = min(scored_population, key=lambda item: item[0])
        return best_state, best_cost

    def initial_population(self, initial_state, population_size):
        population = [initial_state]

        while len(population) < population_size:
            population.append(self.random_individual())

        return population

    def random_individual(self):
        valid_positions = self.valid_positions()
        max_count = min(self.max_sensors, len(valid_positions))

        if max_count <= 0:
            return []

        sensor_count = random.randint(1, max_count)
        return random.sample(valid_positions, sensor_count)

    def reproduce(self, parent1, parent2):
        parent1 = list(parent1)
        parent2 = list(parent2)
        n = len(parent1)

        if n == 0:
            return self.random_individual()

        c = random.randint(1, n)
        child = parent1[:c] + parent2[c:]

        return self.clean_individual(child)

    def mutate(self, individual):
        individual = self.clean_individual(individual)

        if not individual:
            return self.random_individual()

        operation = random.choice(["add", "remove", "replace"])

        if operation == "add" and len(individual) < self.max_sensors:
            positions = [
                position
                for position in self.valid_positions()
                if position not in individual
            ]
            if positions:
                individual.append(random.choice(positions))

        elif operation == "remove" and len(individual) > 1:
            sensor = random.choice(individual)
            individual = [position for position in individual if position != sensor]

        else:
            positions = [
                position
                for position in self.valid_positions()
                if position not in individual
            ]
            if positions:
                index = random.randrange(len(individual))
                individual[index] = random.choice(positions)

        return self.clean_individual(individual)

    def clean_individual(self, individual):
        clean = []

        for position in individual:
            if position not in clean and self.position_valid(*position):
                clean.append(position)

            if len(clean) >= self.max_sensors:
                break

        return clean
