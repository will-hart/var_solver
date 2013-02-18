"""
GraphVariable is a variable wrapper class for the Graph Variable Solver 
module.

Code: William Hart (11082131@brookes.ac.uk)
License: MIT
"""

import logging
from sympy import S, Symbol

logger = logging.getLogger(__name__)


class GraphVariable(object):
    """
    A basic class for representing relationships between variables
    Relationships can be defined using variable names and "solved" 
    for a given set of inputs.

    The dependent and independent variables are determined as 
    well as a the dependency graph.

    The Python library "sympy" (in particular sympify) is used to parse 
    the variables which means that a wide range of expressions are possible.
    For instance a valid expression would be:

        (A_Var + Another_Var)/(2 * A_Third_Var^2)

    Note that Python uses `**` for powers, not the more common `^`.  As Sympy 
    automatically converts these operators, use of either is permitted.

    """

    _name = ""                      # the name of this symbol
    _relationship = ""              # the raw relationship
    _depends_on = []                # symbol names this depends on
    _expression = None              # Sympy expression

    def __init__(self, name, reln=None):
        """Sets the name and optionally relationship for this variable"""
        self._name = name
        self._relationship = reln
        self._depends_on = []
        self._expression = None
        if reln: 
            self._derive(reln)

    def _derive(self, reln):
        """
        Used by the client to define the relationship that describes
        this variable
        """
        self._expression = S(reln)
        self._depends_on = sorted([str(x) for x in self._expression.atoms(Symbol)])

    def solve(self, input_vars):
        """
        Takes a dictionary of input vars and calculates the output value
        based on the relationship.  This value is saved to the dictionary
        and the dictionary is returned
        """
        logger.debug("Solving %s = %s" % (self._name, 
            self._relationship if self._relationship else input_vars[self._name]))

        # check if we have anything to solve
        if not self._relationship:
            return input_vars

        # build up the input variable dictionary
        inputs = {}
        for k in self._depends_on:
            if k not in input_vars:
                raise AttributeError("Missing argument - expected %s in argument dictionary" % k)
            else:
                inputs[k] = input_vars[k]

        # perform the calculation
        op = self._expression.subs(inputs)
        logger.debug("     = %s" % op)
        
        # update the dictionary and return
        input_vars[self._name] = op
        return input_vars
    
    def get_name(self):
        """Gets the name of this variable"""
        return self._name
        
    def get_dependency_list(self):
        """Returns a list of variable dependencies for this variable"""
        return [[x, self._name] for x in self._depends_on]