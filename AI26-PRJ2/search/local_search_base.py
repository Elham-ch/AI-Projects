import random
from collections import Counter

from env import utils as env_utils


class LocalSearchBase:

    COVERAGE_WEIGHT = 10
    SENSOR_WEIGHT = 1

    def __init__(self, world):
        self.world = world
        self.sensor_range = getattr(
            world, "range_sensor", getattr(world, "sensor_range", 0)
        )
        self.max_sensors = getattr(
            world, "sensors_max", getattr(world, "max_sensors", 0)
        )
        self.position_valid = getattr(world, "is_valid_position", None)
        if self.position_valid is None:
            self.position_valid = world.is_valid_position
        self.position_random = getattr(env_utils, "random_poistion", None)
        if self.position_random is None:
            self.position_random = env_utils.random_position
        targets_get = getattr(world, "get_targets", None)
        if targets_get is None:
            targets_get = world.get_targets
        self.targets = list(targets_get())
        self._valid_positions_cache = None

    def valid_positions(self):
        if self._valid_positions_cache is None:
            positions = []
            for x in range(self.world.rows):
                for y in range(self.world.cols):
                    if self.position_valid(x, y):
                        positions.append((x, y))
            self._valid_positions_cache = positions
        return self._valid_positions_cache

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

    def _covered_cells_counter(self, state):
        counts = Counter()
        for sensor in state:
            sx, sy = sensor
            for dx in range(-self.sensor_range, self.sensor_range + 1):
                remaining = self.sensor_range - abs(dx)
                for dy in range(-remaining, remaining + 1):
                    cell = (sx + dx, sy + dy)
                    if self.position_valid(*cell):
                        counts[cell] += 1
        return counts

    def _target_coverage_counter(self, state):
        counts = Counter()
        for sensor in state:
            for target in self.targets:
                if self.covers(sensor, target):
                    counts[target] += 1
        return counts

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

        targets = self.targets
        target_coverage = self._target_coverage_counter(state)
        uncovered_count = sum(1 for target in targets if target_coverage[target] == 0)

        covered_cells = self._covered_cells_counter(state)
        overlap_tile_count = sum(max(0, count - 1) for count in covered_cells.values())

        uncovered_target_cost = uncovered_count * 200
        overlap_tile_cost = overlap_tile_count * 1
        sensor_usage_cost = len(state) * 10

        return uncovered_target_cost + overlap_tile_cost + sensor_usage_cost

    def get_neighbor(self, state):

        neighbors = self.generate_neighbors(state, max_neighbors=40)
        if not neighbors:
            return list(state)
        return random.choice(neighbors)

    def generate_neighbors(self, state, max_neighbors=100):
        current = list(state)
        current_set = set(current)
        neighbors = []
        seen = {tuple(current)}

        def add_neighbor(candidate):
            candidate = list(candidate)
            key = tuple(sorted(candidate))
            if key not in seen and len(candidate) <= self.max_sensors:
                seen.add(key)
                neighbors.append(candidate)

        for sensor in current:
            add_neighbor([position for position in current if position != sensor])

        add_limit = max(8, max_neighbors // 3)
        move_limit = max(12, max_neighbors // 3)
        reposition_limit = max(8, max_neighbors // 5)
        two_sensor_limit = max(5, max_neighbors // 8)

        additions_created = 0
        if len(current) < self.max_sensors:
            for position in self._candidate_positions_for_add(current):
                if position not in current_set:
                    add_neighbor(current + [position])
                    additions_created += 1
                    if additions_created >= add_limit:
                        break

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        moves_created = 0
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
                    moves_created += 1
                    if moves_created >= move_limit:
                        break
            if moves_created >= move_limit:
                break

        for _ in range(reposition_limit):
            if not current:
                break
            index = random.randrange(len(current))
            new_position = random.choice(self.valid_positions())
            if new_position in current_set:
                continue
            candidate = list(current)
            candidate[index] = new_position
            add_neighbor(candidate)

        for _ in range(two_sensor_limit):
            if len(current) < 2:
                break
            i, j = random.sample(range(len(current)), 2)
            candidate = list(current)
            available = [
                p
                for p in self._candidate_positions_for_add(current)
                if p not in current_set
            ]
            if len(available) < 2:
                available = [p for p in self.valid_positions() if p not in current_set]
            if len(available) < 2:
                continue
            candidate[i], candidate[j] = random.sample(available, 2)
            add_neighbor(candidate)

        if len(neighbors) > max_neighbors:
            return random.sample(neighbors, max_neighbors)
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

        valid_positions = self.valid_positions()
        if not valid_positions or self.max_sensors <= 0:
            return []

        state = []
        target_goal = min(self.max_sensors, len(valid_positions))

        while len(state) < target_goal:
            candidates = [
                p for p in self._candidate_positions_for_add(state) if p not in state
            ]
            if not candidates:
                break

            scored = sorted(
                candidates,
                key=lambda p: self._new_targets_covered_by(p, state),
                reverse=True,
            )
            best_score = self._new_targets_covered_by(scored[0], state)
            if best_score <= 0:
                break
            top = [
                p
                for p in scored[:10]
                if self._new_targets_covered_by(p, state) == best_score
            ]
            state.append(random.choice(top))

        if not state:
            state.append(self.position_random(self.world))

        return list(state)

    def _new_targets_covered_by(self, position, state):
        already_covered = self.covered_targets(state)
        return sum(
            1
            for target in self.targets
            if target not in already_covered and self.covers(position, target)
        )
