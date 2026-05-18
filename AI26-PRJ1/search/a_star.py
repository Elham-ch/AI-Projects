import itertools
from queue import PriorityQueue
from typing import List
from env.domain import GameState


def a_star(initial_state: GameState) -> List[str]:
    def heuristic(state: GameState):
        targets = state.get_targets_positions()
        if not targets:
            return 0

        agent_pos = state.get_agent_position()

        nearest = None
        for target in targets:
            distance = abs(agent_pos[0] - target[0]) + abs(agent_pos[1] - target[1])
            if nearest is None or distance < nearest:
                nearest = distance

        return nearest

    frontier = PriorityQueue()
    counter = itertools.count()
    frontier.put((0, next(counter), initial_state))
    came_from = {initial_state: (None, None)}
    cost_so_far = {initial_state: 0}
    goal_state = None

    while not frontier.empty():
        current_state = frontier.get()[2]

        if current_state.is_goal_state():
            goal_state = current_state
            break

        for action, step_cost, next_state in current_state.get_successors():
            new_cost = cost_so_far[current_state] + step_cost
            if (next_state not in came_from or new_cost < cost_so_far[next_state]) and not next_state.is_collision_state():
                cost_so_far[next_state] = new_cost
                priority = new_cost + heuristic(next_state)
                frontier.put((priority, next(counter), next_state))
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
