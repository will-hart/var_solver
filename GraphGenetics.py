import random
import warnings
from GraphExceptions import ConfigurationException

class GenomeBase(object):
    """
    A base genome class with an integer 1D list and mutator, crossover methods
    """
    
    _genome_list = {}
    """
    Holds a 1d list of genome values
    """

    _fitness = 0
    """
    The fitness value for this genome
    """
    
    _graph_manager = None
    """
    The GraphManager class used to calculate the fitness
    """
    
    _min = 0
    """
    The minimum allowable value
    """
    
    _max = 9
    """
    The maximum allowable value
    """
    
    def __init__(self, graph_manager=None, num=10, min=0, max=9, labels=[]):
        
        # reset default values
        self._genome_list = {}
        self._fitness = 0
        self._graph_manager = graph_manager
        self._min = min
        self._max = max

        random.seed()

        # check if we have labels and they are the correct length
        if labels:
            if len(labels) != num:
                raise ConfigurationException("The number of labels is not the same as the number of values generated")

        # check if we have a graph manager passed, then get all the values and labels from it
        # this overrides any other configuration
        if graph_manager:
        
            # if we have also set the labels, warn that this is overriden
            if labels:
                warnings.warn("When initialising GenomeBase, values for labels will be overriden by passing a GraphManager", UserWarning)

            # get the length and labels from the graph manager
            labels = graph_manager.get_missing_vars()
            num = len(labels)

        # set some default values if required
        for i in range(0, num):
            if labels:
                j = labels[i]
            else:
               j = i
            self._genome_list[j] = random.randint(min, max)
    
    def genome_length(self):
        """Returns the number of elements in the genome list"""
        return len(self._genome_list)

    def genome_list(self):
        """Returns the internal genome list of this object"""
        return self._genome_list

    def copy(self):
        """Performs a copy of a GenomeBase, returning indepdent genome lists"""
        g = GenomeBase()
        g._genome_list = self._genome_list.copy()
        g._graph_manager = self._graph_manager
        g._min = self._min
        g._max = self._max
        return g

    def fitness(self, fitness_name="fitness"):
        """
        Returns the fitness of the genome.  If no GraphManager is supplied, 
        return the sum of the individual chromosomes.  Otherwise solve the 
        GraphManager variables and use the "fitness" variable from the results.
        """
        fitness = 0
        if self._graph_manager == None:
            for g in self._genome_list.keys():
                fitness += self._genome_list[g]
        else:
            result = self._graph_manager.resolve(self._genome_list, False)
            fitness = result[fitness_name]

        return fitness

    def mutate(self, chance=0.05, specific_seed=None):
        """
        Randomly mutates chromosomes in the genome list by checking against the 
        chance of mutation for each item. Returns the number of elements that 
        were mutated
        """
        if specific_seed:
            # primarily used for testing purposes :/
            random.seed(specific_seed)
        else:
            random.seed()
        mutated = 0

        # check all keys and randomly mutate some
        for g in self._genome_list.keys():
            if random.random() < chance:
                self._genome_list[g] = random.randint(self._min, self._max)
                mutated += 1

        return mutated