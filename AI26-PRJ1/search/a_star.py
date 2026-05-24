import itertools
from queue import PriorityQueue
from typing import List
from env.domain import GameState
from env.constants import DIRECTIONS


def cached_dijkstra_distance(state: GameState, source_pos, target_pos, cache) -> int:
    if (source_pos, target_pos) in cache:
        return cache[(source_pos, target_pos)]
    distance = dijkstra_distance(state, source_pos, target_pos)
    cache[(source_pos, target_pos)] = distance
    return distance


def dijkstra_distance(state: GameState, source_pos, target_pos) -> int:
    rows, cols = state.get_grid_size()
    crates = state.get_crates_positions()
    frontier = PriorityQueue()
    counter = itertools.count()
    frontier.put((0, next(counter), source_pos))
    cost_so_far = {source_pos: 0}

    while not frontier.empty():
        current_cost, _, current_pos = frontier.get()

        if current_cost != cost_so_far[current_pos]:
            continue

        if current_pos == target_pos:
            return current_cost

        for dr, dc in DIRECTIONS.values():
            next_pos = (current_pos[0] + dr, current_pos[1] + dc)
            in_bounds = 0 <= next_pos[0] < rows and 0 <= next_pos[1] < cols

            if not in_bounds or next_pos in crates:
                continue

            new_cost = current_cost + state.get_terrain_cost(next_pos)
            if new_cost < cost_so_far.get(next_pos, float("inf")):
                cost_so_far[next_pos] = new_cost
                frontier.put((new_cost, next(counter), next_pos))

    return float("inf")


def mst_cost(state: GameState, points, cache) -> int:
    if len(points) <= 1:
        return 0

    root = points[0]
    unvisited = set(points)
    unvisited.remove(root)
    total_cost = 0

    best_cost = {
        point: cached_dijkstra_distance(state, root, point, cache)
        for point in unvisited
    }

    while len(unvisited) > 0:
        next_point = min(unvisited, key=lambda point: best_cost[point])
        total_cost += best_cost[next_point]
        unvisited.remove(next_point)

        for other_point in unvisited:
            edge_cost = cached_dijkstra_distance(state, next_point, other_point, cache)
            if edge_cost < best_cost[other_point]:
                best_cost[other_point] = edge_cost

    return total_cost


def weapon_awareness_key(state: GameState, cache):
    if state.has_weapon() or not state.is_enemy_alive():
        return (0, 0)

    weapon_pos = state.get_weapon_position()
    if weapon_pos is None:
        return (0, 0)

    weapon_distance = cached_dijkstra_distance(
        state, state.get_agent_position(), weapon_pos, cache
    )
    return (1, weapon_distance)


def targets_cost_lower_bound(state: GameState, source_pos, cache) -> int:
    targets_pos = list(state.get_targets_positions())
    if len(targets_pos) == 0:
        return 0

    nearest_distance = min(
        cached_dijkstra_distance(state, source_pos, target_pos, cache)
        for target_pos in targets_pos
    )
    return nearest_distance + mst_cost(state, targets_pos, cache)


def target_triple_lower_bound(state: GameState, source_pos, distance_cache, triple_cache):
    targets_pos = list(state.get_targets_positions())
    if len(targets_pos) < 3:
        return 0

    cache_key = (source_pos, frozenset(targets_pos))
    if cache_key in triple_cache:
        return triple_cache[cache_key]

    best_lower_bound = 0
    for target_triple in itertools.combinations(targets_pos, 3):
        best_triple_cost = float("inf")
        for first, second, third in itertools.permutations(target_triple):
            triple_cost = (
                cached_dijkstra_distance(state, source_pos, first, distance_cache)
                + cached_dijkstra_distance(state, first, second, distance_cache)
                + cached_dijkstra_distance(state, second, third, distance_cache)
            )
            if triple_cost < best_triple_cost:
                best_triple_cost = triple_cost

        if best_triple_cost > best_lower_bound:
            best_lower_bound = best_triple_cost

    triple_cache[cache_key] = best_lower_bound
    return best_lower_bound


def a_star(initial_state: GameState) -> List[str]:
    frontier = PriorityQueue()
    counter = itertools.count()
    came_from = {initial_state: (None, None)}
    cost_so_far = {initial_state: 0}
    goal_state = None
    cache = {}
    triple_cache = {}

    def heuristic(state: GameState) -> int:
        agent_pos = state.get_agent_position()
        direct_cost = targets_cost_lower_bound(state, agent_pos, cache)

        if state.has_weapon() or not state.is_enemy_alive():
            return max(
                direct_cost,
                target_triple_lower_bound(state, agent_pos, cache, triple_cache),
            )

        weapon_pos = state.get_weapon_position()
        if weapon_pos is None:
            return max(
                direct_cost,
                target_triple_lower_bound(state, agent_pos, cache, triple_cache),
            )

        weapon_cost = cached_dijkstra_distance(
            state, agent_pos, weapon_pos, cache
        ) + targets_cost_lower_bound(state, weapon_pos, cache)
        weapon_aware_cost = min(direct_cost, weapon_cost)
        triple_cost = target_triple_lower_bound(
            state,
            agent_pos,
            cache,
            triple_cache,
        )
        return max(weapon_aware_cost, triple_cost)

    initial_h = heuristic(initial_state)
    frontier.put(
        (
            initial_h,
            weapon_awareness_key(initial_state, cache),
            initial_h,
            0,
            next(counter),
            initial_state,
        )
    )

    while not frontier.empty():
        _, _, _, popped_cost, _, current_state = frontier.get()

        if popped_cost != cost_so_far[current_state]:
            continue

        if current_state.is_goal_state():
            goal_state = current_state
            break

        for action, step_cost, next_state in current_state.get_successors():
            new_cost = cost_so_far[current_state] + step_cost
            if (
                next_state not in came_from or new_cost < cost_so_far[next_state]
            ) and not next_state.is_collision_state():
                cost_so_far[next_state] = new_cost
                h = heuristic(next_state)
                priority = new_cost + h
                frontier.put(
                    (
                        priority,
                        weapon_awareness_key(next_state, cache),
                        h,
                        new_cost,
                        next(counter),
                        next_state,
                    )
                )
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
