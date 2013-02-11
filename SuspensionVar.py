class SuspensionVar(object):
    """
    A basic class for representing relationships between variables
    in suspension geometry. Relationships can be defined using 
    variable names and "solved" for a given set of inputs.

    The dependent and independent variables are determined as 
    well as a the dependency graph.

    To be correctly solved, the equation must be passed in the form

        ( VAR + D ) / WS + ( QX - Z * D )

    Note there is a space between each  variable name and operator.
    Allowable operators are +, -, /, *, ( and ). Direct integers and
    floats (e.g 2x) are not allowed - use a variable constant instead 
    and define at run time.  

    Variables may have any name, but simple strings are recommended.

    Code: William Hart (11082131@brookes.ac.uk)
    License: MIT
    """

    _name = ""
    _derived = False
    _relationship = ""
    _built_relationship = ""
    _depends_on = []
    _operators = ["+", "-", "*", "/", "(", ")"]

    def __init__(self, name, reln=None):
        """Sets the name and optionally relationship for this variable"""
        self._name = name
        self._derived = False
        self._relationship = ""
        self._built_relationship = ""
        self._depends_on = []
        if reln: 
            self.derive(reln)

    def derive(self, reln):
        """
        Used by the client to define the relationship that describes
        this variable
        """
        self._derived = True
        self._relationship = reln
        
        ops  = [x.strip() for x in self._relationship.split(" ")]
        self._determine_dependency(ops)
        
        # Build the relationship using dictionary operators
        self._built_relationship = ""
        for i, v in enumerate(ops):
            if ops[i] not in self._operators:
                # if not an operator wrap in "inputs" dictionary
                ops[i] = "inputs['%s']" % ops[i]
        
        # rejoin the list into an equation to solve
        self._built_relationship = " ".join(ops)

    def _determine_dependency(self, d_vars):
        """
        Determines the variables that this variable depends on
        
        Takes a list of equation terms (by splitting relationship
        by "  ") as the d_vars argument
        """
        # remove operators and save
        for i, v in enumerate(d_vars):
            if d_vars[i] not in self._operators:
                self._depends_on.append(d_vars[i])

    def solve(self, input_vars):
        """
        Takes a dictionary of input vars and calculates the output value
        based on the relationship.  This value is saved to the dictionary
        and the dictionary is returned
        """
        print "Solving %s = %s" % (self._name, 
            self._relationship if self._relationship else input_vars[self._name])

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
        op = eval(self._built_relationship)
        print "     = %s" % op
        
        # update the dictionary and return
        input_vars[self._name] = op
        return input_vars
    
    def get_name(self):
        """Gets the name of this variable"""
        return self._name
        
    def get_dependency_list(self):
        """Returns a list of variable dependencies for this variable"""
        return [[x, self._name] for x in self._depends_on]