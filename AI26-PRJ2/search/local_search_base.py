import random


class LocalSearchBase:

    COVERAGE_WEIGHT = 10
    SENSOR_WEIGHT = 1

    def __init__(self, world):
        self.world = world
        self.targets = world.get_targets()
        self.num_targets = len(self.targets)

    def covers(self, sensor, target):
        sx, sy = sensor
        tx, ty = target
        return abs(sx - tx) + abs(sy - ty) <= self.world.sensor_range

    def count_covered_targets(self, state):
        covered = 0
        for target in self.targets:
            for sensor in state:
                if self.covers(sensor, target):
                    covered += 1
                    break
        return covered

    def evaluate(self, state):
        covered = self.count_covered_targets(state)
        uncovered = self.num_targets - covered

        cost = (self.COVERAGE_WEIGHT * uncovered
                + self.SENSOR_WEIGHT * len(state))
        return cost

    def _random_free_position(self, occupied, max_tries=100):
        occupied = set(occupied)
        for _ in range(max_tries):
            x = random.randint(0, self.world.rows - 1)
            y = random.randint(0, self.world.cols - 1)
            if self.world.is_valid_position(x, y) and (x, y) not in occupied:
                return (x, y)
        return None

    def get_neighbor(self, state):
    
        state = list(state)

        can_move = len(state) >= 1
        can_add = len(state) < self.world.max_sensors
        can_remove = len(state) > 1

        operations = []
        if can_move:
            operations += ["move"] * 3
        if can_add:
            operations += ["add"] * 1
        if can_remove:
            operations += ["remove"] * 1

        if not operations:                   
            return state

        op = random.choice(operations)

        if op == "move":
            idx = random.randrange(len(state))
            new_pos = self._random_free_position(
                occupied=state[:idx] + state[idx + 1:]
            )
            if new_pos is not None:
                state[idx] = new_pos

        elif op == "add":
            new_pos = self._random_free_position(occupied=state)
            if new_pos is not None:
                state.append(new_pos)

        elif op == "remove":
            idx = random.randrange(len(state))
            state.pop(idx)

        return state

    def initialize_state(self):
        k = random.randint(1, self.world.max_sensors)

        state = []
        for _ in range(k):
            pos = self._random_free_position(occupied=state)
            if pos is None:
                break
            state.append(pos)

        if not state:
            pos = self._random_free_position(occupied=[])
            if pos is not None:
                state.append(pos)

        return state