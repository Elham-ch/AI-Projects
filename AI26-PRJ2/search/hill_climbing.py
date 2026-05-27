from search.local_search_base import LocalSearchBase


class HillClimbing(LocalSearchBase):
    def run(self, initial_state, **kwargs):
        """
        TODO: Implement the Hill Climbing algorithm.
        
        Parameters
        ----------
        initial_state : list of tuples
            The initial configuration of sensors.
        **kwargs : 
            Define and add any other parameters you might need for the algorithm 

        Returns
        -------
        best_state : list of tuples
            The best configuration found.
        best_cost : int or float
            The cost of the best configuration.
        evaluations : list
            List of costs at each iteration (used for plotting).
        states_history : list of lists
            List of states at each iteration (used for animation).
        """
        
        raise NotImplementedError("Students must implement this method.")