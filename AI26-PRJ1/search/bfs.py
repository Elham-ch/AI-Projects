from collections import deque
from typing import List


def bfs(initial_state) -> List[str]:
    frontier = deque([(initial_state, [])])
    
    visited = set()
    
    while frontier:
        current_state, path = frontier.popleft()
        

        if current_state.is_goal_state():
            return path

        state_hash = hash(current_state)
        if state_hash in visited:
            continue

        visited.add(state_hash)

        for action, step_cost, next_state in current_state.get_successors():
            next_hash = hash(next_state)

            if next_hash in visited or next_state.is_collision_state():
                continue

            new_path = path + [action]


            frontier.append((next_state, new_path))
    
    return []
