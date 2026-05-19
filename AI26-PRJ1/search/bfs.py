from typing import List
from collections import deque
from env.domain import GameState


def bfs(initial_state: GameState) -> List[str]:
    frontier = deque([initial_state])
    came_from = {initial_state: (None, None)}
    goal_state = None

    while frontier:
        current_state = frontier.popleft()

        if current_state.is_goal_state():
            goal_state = current_state
            break

        for action, _, next_state in current_state.get_successors():
            if next_state not in came_from and not next_state.is_collision_state():
                frontier.append(next_state)
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
