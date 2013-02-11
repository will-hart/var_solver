import argparse
from SuspensionVarManager import SuspensionVarManager

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
args = parser.parse_args()

# get the json from the file
raw_json = ""
with open(args.datafile) as f:
    raw_json = f.read()

# Solve and print output to screen
vm = SuspensionVarManager()
vm.load_json(raw_json)
result = vm.resolve(args.no_plot)

# check if we are printing or outputting results
if args.out:
    with open(args.out, 'w') as f:
        f.write(result)
else:
    print result