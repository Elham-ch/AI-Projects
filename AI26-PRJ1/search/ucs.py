import heapq
from typing import List


def ucs(initial_state) -> List[str]:
    
    frontier = []
    counter = 0
    
    heapq.heappush(frontier, (0, counter, initial_state, []))
    counter += 1
    
    visited = set()
    
    while frontier:
        g_cost, _, current_state, path = heapq.heappop(frontier)

        if current_state.is_collision_state():
            continue
        
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
            
            new_cost = g_cost + step_cost
            new_path = path + [action]
            
            heapq.heappush(
                frontier,
                (new_cost, counter, next_state, new_path)
            )
            counter += 1
    
    return []
