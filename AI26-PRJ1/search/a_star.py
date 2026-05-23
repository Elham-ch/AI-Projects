import itertools
from queue import PriorityQueue
from typing import List
from env.domain import GameState


def a_star(initial_state: GameState) -> List[str]:
    def manhattan(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def mst_cost(points):
        if len(points) <= 1:
            return 0

        remaining = set(points)
        current = remaining.pop()
        visited = {current}
        total_cost = 0

        while remaining:
            best_distance = None
            best_point = None

            for source in visited:
                for target in remaining:
                    distance = manhattan(source, target)
                    if (
                        best_distance is None
                        or distance < best_distance
                    ):
                        best_distance = distance
                        best_point = target

            total_cost += best_distance
            visited.add(best_point)
            remaining.remove(best_point)

        return total_cost

    def targets_lower_bound(start_pos, targets):
        if not targets:
            return 0

        nearest = min(
            manhattan(start_pos, target)
            for target in targets
        )

        return 5 * (nearest + mst_cost(targets))

    def heuristic(state: GameState):
        targets = list(state.get_targets_positions())
        if not targets:
            return 0

        agent_pos = state.get_agent_position()
        direct_cost = targets_lower_bound(agent_pos, targets)

        if state.has_weapon() or not state.is_enemy_alive():
            return direct_cost

        weapon_pos = state.get_weapon_position()
        if weapon_pos is None:
            return direct_cost

        weapon_cost = (
            50 * manhattan(agent_pos, weapon_pos)
            + targets_lower_bound(weapon_pos, targets)
        )

        return min(direct_cost, weapon_cost)

    frontier = PriorityQueue()
    counter = itertools.count()
    initial_priority = heuristic(initial_state)
    frontier.put((initial_priority, 0, next(counter), initial_state))
    came_from = {initial_state: (None, None)}
    cost_so_far = {initial_state: 0}
    goal_state = None

    while not frontier.empty():
        current_state = frontier.get()[3]
        if current_state.is_goal_state():
            goal_state = current_state
            break

        for action, step_cost, next_state in current_state.get_successors():
            new_cost = cost_so_far[current_state] + step_cost
            if (next_state not in came_from or new_cost < cost_so_far[next_state]) and not next_state.is_collision_state():
                cost_so_far[next_state] = new_cost
                priority = new_cost + heuristic(next_state)
                frontier.put((priority, new_cost, next(counter), next_state))
                came_from[next_state] = (current_state, action)

    if goal_state is None:
        return []

    path = []
    curr = goal_state
    while curr is not None:
        prev, action = came_from[curr]
        if action is not None:
            path.append(action)
        curr = prev
    path.reverse()
    return path
