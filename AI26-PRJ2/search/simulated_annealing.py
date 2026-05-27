from search.local_search_base import LocalSearchBase


class SimulatedAnnealing(LocalSearchBase):
    def run(self, initial_state, **kwargs):
        """
        TODO: Implement the Simulated Annealing algorithm.
        
        Parameters
        ----------
        initial_state : list of tuples
            The initial configuration of sensors.
        **kwargs : 
            Define and add all necessary parameters required for Simulated Annealing 

        Returns
        -------
        best_state : list of tuples
        best_cost : int or float
        evaluations : list
        states_history : list of lists
        """
        
        raise NotImplementedError("Students must implement this method.")