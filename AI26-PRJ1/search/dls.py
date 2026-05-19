from typing import List

CUTOFF = "cutoff"
FAILURE = "failure"


def _state_key(state):
    return (
        state.get_agent_position(),
        frozenset(state.get_targets_positions()),
        state.get_enemy_cycle(),
        state.has_weapon(),
        state.is_enemy_alive(),
    )


def depth_limited_search(initial_state, limit):
    start_key = _state_key(initial_state)
    frontier = [(initial_state, [], 0)]
    best_depth = {start_key: 0}
    result = FAILURE

    while frontier:
        state, actions, depth = frontier.pop()

        if state.is_goal_state():
            return actions

        if depth > limit:
            result = CUTOFF
            continue

        for action, _, next_state in reversed(state.get_successors()):
            if next_state.is_collision_state():
                continue

            key = _state_key(next_state)
            new_depth = depth + 1

            if new_depth >= best_depth.get(key, float("inf")):
                continue
            best_depth[key] = new_depth

            frontier.append((next_state, actions + [action], new_depth))

    return result


def dls(initial_state, limit=None) -> List[str]:

    if initial_state.is_goal_state():
        return []

    if limit is not None:
        result = depth_limited_search(initial_state, limit)
        return result if isinstance(result, list) else []

    rows, cols = initial_state.get_grid_size()
    max_depth = rows * cols 

    for depth in range(max_depth + 1):
        result = depth_limited_search(initial_state, depth)
        if result == CUTOFF:
            continue
        if result == FAILURE:
            return []
        return result  

    return []