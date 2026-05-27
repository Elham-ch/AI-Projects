class LocalSearchBase:
    def __init__(self, world):
        self.world = world

    def evaluate(self, state):
        """
        TODO: Implement the evaluation (Cost) function.
        
        Design a function that calculates the cost of the current sensor placement.
        Refer to the project documentation for the primary objectives and constraints.
        
        Returns:    
            cost (int or float): The evaluated cost of the state (lower is better).
        """
        raise NotImplementedError("Students must implement this method.")

    def get_neighbor(self, state):
        """
        TODO: Implement the neighbor generation function.
        
        Generate a new valid state by applying a local change to the current state.
        Ensure you include all the required operations mentioned in the project PDF
        to support a dynamic search space.
        
        Returns:
            neighbor_state (list of tuples): The newly generated valid state.
        """
        raise NotImplementedError("Students must implement this method.")

    def initialize_state(self):
        """
        TODO: Generate a valid initial state.
        
        Create a starting configuration of sensors within the grid boundaries,
        respecting the maximum sensor limits and obstacle placements.
        
        Returns:
            initial_state (list of tuples): The starting coordinates of the sensors.
        """
        raise NotImplementedError("Students must implement this method.")