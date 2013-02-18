

class SolverException(Exception):
    """A generic exception class used by the GraphManager to report solver errors"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class ConfigurationException(Exception):
    """Used by the GraphManager to report configuration errors of the solver"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
