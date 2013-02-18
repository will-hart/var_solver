"""
A solver for complex, inter-related variables.  Builds a graph
of the variable inputs and solves them in an intelligent order.

Code: William Hart (hart.wl@gmail.com)
License: MIT
"""
import argparse
from GraphManager import GraphManager

# parse the arguments
parser = argparse.ArgumentParser(description="Solves complex relationships between variables")
parser.add_argument('datafile', type=str, help="The JSON encoded file name containing variable data")
parser.add_argument('-n', '--no-plot',
    action="store_false",
    default=True,
    help="Set this flag to disable generation of graph PDF files"
)
parser.add_argument('-o', "--out",
    metavar='outfile',
    help="If a filename is provided, write output here",
    default=None
)
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Show verbose messages")
args = parser.parse_args()

# get the json from the file
print "Loading JSON data from %s" % args.datafile
raw_json = ""
with open(args.datafile) as f:
    raw_json = f.read()

# create the variable manager
vm = GraphManager()

# check for verbose flag
if args.verbose:
    vm.set_verbose()

# Solve and print output to screen
vm.load_json(raw_json)
vm.resolve(args.no_plot)

# check if we are printing or outputting results
if args.out:
    with open(args.out, 'w') as f:
        f.write(vm.get_output())
else:
    print vm.get_output()
    

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