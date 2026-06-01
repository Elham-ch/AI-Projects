import random

from env import utils as env_utils


class LocalSearchBase:
    def __init__(self, world):
        self.world = world
        self.sensor_range = world.sensor_range
        self.max_sensors = world.max_sensors
        self.position_valid = world.is_valid_position
        self.position_random = env_utils.random_position
        self.targets = world.get_targets()
        self._valid_positions_cache = None

    def valid_positions(self):
        positions = []
        for x in range(self.world.rows):
            for y in range(self.world.cols):
                if self.position_valid(x, y):
                    positions.append((x, y))
        return positions

    def distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def covers(self, sensor, position):
        return self.distance(sensor, position) <= self.sensor_range

    def covered_targets(self, state):
        covered = set()
        for target in self.targets:
            if any(self.covers(sensor, target) for sensor in state):
                covered.add(target)
        return covered

    def _overlap_tile_count(self, state):
        covered_cells = set()
        overlap_count = 0
        for sensor in state:
            sx, sy = sensor
            for dx in range(-self.sensor_range, self.sensor_range + 1):
                remaining = self.sensor_range - abs(dx)
                for dy in range(-remaining, remaining + 1):
                    cell = (sx + dx, sy + dy)
                    if self.position_valid(*cell):
                        if cell in covered_cells:
                            overlap_count += 1
                        else:
                            covered_cells.add(cell)
        return overlap_count

    def _covered_target_count(self, state):
        covered_count = 0
        for target in self.targets:
            for sensor in state:
                if self.covers(sensor, target):
                    covered_count += 1
                    break
        return covered_count

    def evaluate(self, state):
        """
        Evaluate a sensor placement. Lower cost is better.

        The heuristic cost is an additive penalty:

        1. uncovered targets: every missed target is expensive
        2. overlap tiles: repeated coverage wastes sensing area
        3. used sensors: fewer sensors are preferred when coverage is similar

        Returns:
            cost (int or float): The evaluated cost of the state (lower is better).
        """

        covered_target_count = self._covered_target_count(state)
        uncovered_count = len(self.targets) - covered_target_count

        overlap_tile_count = self._overlap_tile_count(state)

        uncovered_target_cost = uncovered_count * 200
        sensor_usage_cost = len(state) * 10
        overlap_tile_cost = overlap_tile_count * 1

        return uncovered_target_cost + overlap_tile_cost + sensor_usage_cost

    def get_random_neighbor(self, state):
        neighbors = self.generate_neighbors(state)
        if not neighbors:
            return list(state)
        return random.choice(neighbors)

    def generate_neighbors(self, state):
        current = list(state)
        current_set = set(current)
        neighbors = []
        seen = {tuple(sorted(current))}

        def add_neighbor(candidate):
            key = tuple(sorted(candidate))
            if key not in seen and len(candidate) <= self.max_sensors:
                seen.add(key)
                neighbors.append(candidate)

        # Remove one sensor.
        for sensor in current:
            add_neighbor([position for position in current if position != sensor])

        candidate_positions = [
            position
            for position in self._candidate_positions_for_add(current)
            if position not in current_set
        ]

        # Add one sensor.
        if len(current) < self.max_sensors:
            for position in candidate_positions:
                add_neighbor(current + [position])

        # Move one sensor to a neighboring cell.
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for index, sensor in enumerate(current):
            sx, sy = sensor
            for dx, dy in directions:
                new_position = (sx + dx, sy + dy)
                if new_position not in current_set and self.position_valid(
                    *new_position
                ):
                    candidate = list(current)
                    candidate[index] = new_position
                    add_neighbor(candidate)

        return neighbors

    def _candidate_positions_for_add(self, state):
        current = list(state)
        uncovered_targets = [
            target
            for target in self.targets
            if target not in self.covered_targets(current)
        ]
        focus_targets = list(uncovered_targets if uncovered_targets else self.targets)

        candidates = []
        seen = set()
        random.shuffle(focus_targets)

        for target in focus_targets:
            tx, ty = target
            for dx in range(-self.sensor_range, self.sensor_range + 1):
                remaining = self.sensor_range - abs(dx)
                for dy in range(-remaining, remaining + 1):
                    position = (tx + dx, ty + dy)
                    if position not in seen and self.position_valid(*position):
                        seen.add(position)
                        candidates.append(position)

        random.shuffle(candidates)
        random_candidates = random.sample(
            self.valid_positions(),
            k=min(len(self.valid_positions()), max(10, self.max_sensors * 2)),
        )
        for position in random_candidates:
            if position not in seen:
                seen.add(position)
                candidates.append(position)

        return candidates

    def initialize_state(self):
        return [self.position_random(self.world)]
