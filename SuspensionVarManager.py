from SuspensionVar import SuspensionVar
import igraph
import json

class SuspensionVarManager(object):
    """
    Builds a list of SuspensionVar objects, calculates a dependency graph
    and then requests inputs for variables which are not dependent on any
    other variable.  

    It then traverses the graph and solves the variables, finally printing 
    the result for the user
    """

    _vars = []  # SuspensionVar objects to be solved
    _graph = None  # dependency digraph
    _results = {}  # generated results
    _inputs = {}  # variables with no dependencies
    _incomplete = True  # is our analysis incomplete

    def add_var(self, name, eq):
        """Builds a new variable and adds it based on a given name and equation"""
        if name in self._vars:
            raise Error("The variable %s is already defined" % name)
        self._vars.append(SuspensionVar(name, eq))

    def resolve(self, plot=True):
        """Resolves the variables based on the given inputs and prints the result"""
        solve_order = self._build_dependency_graph(plot)
        self._traverse_solve(solve_order, self._resolve_inputs(solve_order))
        return self._print_outputs()
    
    def load_json(self, json_str):
        """Loads variable groupings from a json string"""
        print "Loading data from JSON"
        
        # get the json object and check for variables
        obj = json.loads(json_str)
        if "variables" not in obj:
            raise AttributeError("JSON has no 'vars' dictionary - cannot process")
        
        # load in all the vars
        js_vars = obj['variables']
        
        # load the variables
        print " >> Loading variables from JSON"
        for var in js_vars:
            print "      - Loading %s" % var['name']
            if "relationship" in var:
                print "             relationship: %s" % var['relationship']
            if "name" not in var:
                raise AttributeError("Unable to find variable name - %s - aborting load by JSON" % var)
            reln = var['relationship'] if "relationship" in var else None
            self._vars.append(SuspensionVar(var['name'], reln=reln))
        print " >> Variables loaded"

        # load the initial conditions, if present
        print " >> Loading start conditions"
        if "start_conditions" in obj:
            print "      - Some conditions are present"
            start_conds = obj['start_conditions']
            for var in start_conds:
                print "             Loading %s (value %s)" % (var, start_conds[var])
                self._inputs[var] = start_conds[var]
        print " >> Start condition load complete"
        print " >> JSON load complete"

    def _build_dependency_graph(self, plot):
        """Builds up variable dependencies by building a network from the variables"""
        print "Building dependency graph"

        # returns a new graph object containing a minimum spanning tree
        self._graph = igraph.Graph(directed=True)
        
        # add vertices from vars and build edge list
        depend_edges = []
        for v in self._vars:
            self._graph.add_vertex(v.get_name(), obj=v)
            depend_edges += v.get_dependency_list()

        # add edges
        self._graph.add_edges(depend_edges)
        
        # write out the whole dependency graph
        if plot:
            layout = self._graph.layout("kk")
            self._graph.vs['label'] = self._graph.vs['name']
            igraph.plot(self._graph, "dependency_graph.pdf", layout=layout)
        
        # build the spanning tree for solving and write to file
        tree = self._graph.spanning_tree()
        if plot:
            layout = tree.layout("kk")
            tree.vs['label'] = tree.vs['name']
            igraph.plot(tree, "solve_tree_graph.pdf", layout=layout)
        
        # return the solving tree to the caller
        print " >> Dependency graph complete"
        return tree

    def _resolve_inputs(self, tree):
        """Determines variables with no dependencies and gets their starting value"""
        print "Finding missing inputs"
        no_pre = [x for x in tree.vs if x.predecessors() == []]

        # copy all pre-defined inputs across to results
        self._results = self._inputs.copy()

        # work out if any input variables are missing
        for v in no_pre:
            if v['name'] not in self._results:
                self._results[v['name']] = raw_input("Please enter a value for %s: " % v['name'])
        print " >> missing inputs complete"
        return no_pre

    def _traverse_solve(self, tree, initial_roots):
        """Traverses the dependency graph, solving as it goes"""
        print "\n\n\n============================="
        print "       Starting solve"
        print "============================="
        
        # Save initial conditions
        no_pre = initial_roots
        
        # output initial conditions
        print "      INITIAL GIVENS:"
        print ', '.join([x['name'] for x in no_pre])
        print "-----------------------------\n\n"
        
        
        # process until we have leftover variables
        while len(no_pre) > 0:
            # solve each block with no predecessors
            print "Assessing %s variables with no predecessors" % len(no_pre)
            for v in no_pre[:]:
                print " > Consider %s " % v['name']
                self._results = v['obj'].solve(self._results)

            # remove nodes that have been processed
            tree.delete_vertices(no_pre)

            # get new nodes for processing
            print "Determining new variables without predecessors"
            no_pre = [x for x in tree.vs if x.predecessors() == []]
        
        # if we have no nodes left, unset "incomplete" flag
        if len(tree.vs) == 0:
            self._incomplete = False
        print " >> Solve complete"
        
    def _print_outputs(self):
        """Returns the output dictionary in "pretty printed" format"""
        print "Generating output string"
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
        
        for k in self._inputs:
            ret += "           > %s:    %s\n"  %(k, self._inputs[k])
        
        ret += "----------------------------------------------------------\n\n"
        ret += "    RESULTS: \n\n"
        for k in self._results:
            ret += "           > %s:    %s\n"  %(k, self._results[k])
        
        ret += "----------------------------------------------------------\n"

        print " >> output generated"
        return ret