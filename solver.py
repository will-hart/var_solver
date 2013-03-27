"""
A solver for complex, inter-related variables.  Builds a graph
of the variable inputs and solves them in an intelligent order.

Code: William Hart (hart.wl@gmail.com)
License: MIT
"""
import argparse
from GraphManager import GraphManager

def resolve_inputs(manager):
    """Determines variables with no dependencies and gets their starting value"""
    print "resolving missing"
    missing = manager.get_missing_vars()
    missing_dict = {}
    
    # work out if any input variables are missing
    for v in missing:
        missing_dict[v['name']] = S(raw_input("Please enter a value for %s: " % v['name']))
    return missing_dict

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
print "Resolving missing inputs"
init = resolve_inputs(vm)
print "Done with missing inputs"
vm.resolve(init, args.no_plot)

# check if we are printing or outputting results
if args.out:
    with open(args.out, 'w') as f:
        f.write(vm.get_output())
else:
    print vm.get_output()
