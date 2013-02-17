import igraph
import json
import logging
from sympy import S

from SuspensionVar import SuspensionVar

logging.basicConfig()
logger = logging.getLogger(__name__)


class SuspensionVarManager(object):
    """
    Builds a list of SuspensionVar objects, calculates a dependency graph
    and then requests inputs for variables which are not dependent on any
    other variable.  

    It then traverses the graph and solves the variables, finally printing 
    the result for the user.
    
    Code: William Hart (11082131@brookes.ac.uk)
    License: MIT
    """

    _vars = []  # SuspensionVar objects to be solved
    _graph = None  # dependency digraph
    _results = {}  # generated results
    _inputs = {}  # variables with no dependencies
    _incomplete = True  # is our analysis incomplete
    _result_str = "" # A string to hold result output

    def add_var(self, name, eq):
        """Builds a new variable and adds it based on a given name and equation"""
        if name in self._vars:
            raise Error("The variable %s is already defined" % name)
        self._vars.append(SuspensionVar(name, eq))

    def set_verbose(self):
        """Sets verbose logging for the variable manager"""
        logger.setLevel(logging.DEBUG)

    def resolve(self, plot=True):
        """Resolves the variables based on the given inputs and prints the result"""
        self._build_dependency_graph(plot)
        self._traverse_solve(self._resolve_inputs())
        self._generate_outputs()
    
    def load_json(self, json_str):
        """Loads variable groupings from a json string"""
        logger.info("Loading data from JSON")
        
        # get the json object and check for variables
        obj = json.loads(json_str)
        if "variables" not in obj:
            raise AttributeError("JSON has no 'vars' dictionary - cannot process")
        
        # load in all the vars
        js_vars = obj['variables']
        
        # load the variables
        logger.debug(" >> Loading variables from JSON")
        for var in js_vars:
            logger.debug("      - Loading %s" % var['name'])
            if "relationship" in var:
                logger.debug("             relationship: %s" % var['relationship'])
            if "name" not in var:
                raise AttributeError("Unable to find variable name - %s - aborting load by JSON" % var)
            reln = var['relationship'] if "relationship" in var else None
            self._vars.append(SuspensionVar(var['name'], reln=reln))
        logger.debug(" >> Variables loaded")

        # load the initial conditions, if present
        logger.debug(" >> Loading start conditions")
        if "start_conditions" in obj:
            logger.debug("      - Some conditions are present")
            start_conds = obj['start_conditions']
            for var in start_conds:
                logger.debug("             Loading %s (value %s)" % (var, start_conds[var]))
                self._inputs[var] = S(start_conds[var])
        logger.debug(" >> Start condition load complete")
        logger.info(" >> JSON load complete")

    def get_output(self):
        """Returns the result output as a string"""
        return self._result_str

    def _build_dependency_graph(self, plot):
        """Builds up variable dependencies by building a network from the variables"""
        logger.info("Building dependency graph")

        # returns a new graph object containing a minimum spanning tree
        self._graph = igraph.Graph(directed=True)
        
        # add vertices from vars and build edge list
        # do a quick check to make sure we only add 
        # each edge once.
        depend_edges = []
        for v in self._vars:
            self._graph.add_vertex(v.get_name(), obj=v)
            for dep in v.get_dependency_list():
                if dep not in depend_edges:
                    depend_edges.append(dep)

        # add edges
        self._graph.add_edges(depend_edges)
        
        # write out the whole dependency graph
        if plot:
            layout = self._graph.layout("fr")
            self._graph.vs['label'] = self._graph.vs['name']
            igraph.plot(self._graph, "dependencies_0.pdf", layout=layout)
        
        # return the solving tree to the caller
        logger.info(" >> Dependency graph complete")

    def _resolve_inputs(self):
        """Determines variables with no dependencies and gets their starting value"""
        logger.info("Finding missing inputs")
        no_pre = [x for x in self._graph.vs if x.predecessors() == []]

        # copy all pre-defined inputs across to results
        self._results = self._inputs.copy()

        # work out if any input variables are missing
        for v in no_pre:
            if v['name'] not in self._results:
                self._results[v['name']] = S(raw_input("Please enter a value for %s: " % v['name']))               

        logger.info(" >> missing inputs complete")
        return no_pre

    def _traverse_solve(self, initial_roots):
        """Traverses the dependency graph, solving as it goes"""
        logger.debug("=============================")
        logger.info("       Starting solve")
        logger.debug("=============================")
        
        # Save initial conditions
        no_pre = initial_roots
        
        # output initial conditions
        logger.debug("      INITIAL GIVENS:")
        logger.debug(', '.join([x['name'] for x in no_pre]))
        logger.debug("-----------------------------")
        plot_counter = 0
        
        # process until we have leftover variables
        while len(no_pre) > 0:
            # solve each block with no predecessors
            logger.debug("Assessing %s variables with no predecessors" % len(no_pre))
            logger.debug("--------------------------------------------")
            for v in no_pre[:]:
                self._results = v['obj'].solve(self._results)

            # remove nodes that have been processed
            self._graph.delete_vertices(no_pre)
            
            # write new dependency graph if required
            if len(self._graph.vs) > 0:
                plot_counter += 1
                layout = self._graph.layout("fr")
                self._graph.vs['label'] = self._graph.vs['name']
                igraph.plot(self._graph, "dependencies_%s.pdf" % plot_counter, layout=layout)

            # get new nodes for processing
            no_pre = [x for x in self._graph.vs if x.predecessors() == []]
        
        # if we have no nodes left, unset "incomplete" flag
        if len(self._graph.vs) == 0:
            self._incomplete = False
        logger.info(" >> Solve complete")
        
    def _generate_outputs(self):
        """Returns the output dictionary in "pretty printed" format"""
        logger.info("Generating output string")
        ret = ""
        ret += "----------------------------------------------------------\n"
        ret += "             Suspension Variable Solver - OUTPUT \n"
        ret += "----------------------------------------------------------\n\n"
        
        # check if we have incomplete solve
        if self._incomplete:
            ret += "  UNABLE TO SOLVE ALL VARIABLES!\n"
        else: 
            ret += "  SOLVED ALL VARIABLES.\n"
        ret += "----------------------------------------------------------\n"
        
        # write out the results, starting with inputs
        ret += "    INPUTS: \n\n"
        
        for k in sorted(self._inputs.keys()):
            ret += "           >\t%s: %0.4f\n"  %(k, self._inputs[k])
        
        ret += "----------------------------------------------------------\n\n"
        ret += "    RESULTS: \n\n"
        for k in sorted(self._results.keys()):
            ret += "           >\t%s: %0.4f\n"  %(k, self._results[k])
        
        ret += "----------------------------------------------------------\n"

        logger.info(" >> output generated")
        self._result_str = ret