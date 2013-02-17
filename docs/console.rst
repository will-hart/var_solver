Calling from the Console
=========================

A console helper file `solver.py` is supplied for quick testing of
the Graph Solver.  

Getting Help 
------------

You can display a custom help message by typing::

    python solver.py -h

Basic Usage
------------

The most basic usage is to take an input file and print the output to console::

    python solver.py data/sample_data.json

Options
--------

-n, --no-plot
+++++++++++++

Solve without creating PDF outputs for dependency graphs::

    python solver.py -n data/sample_data.json
 
-o, --out
++++++++++

Specify a file name for writing outputs::

    python solver.py -o output.txt data/sample_data.json

Note that this is not compatible with the `--verbose` option.  To write a full
log to a file, including debugging outputs, use::

    python solver.py -v data/sample_data.json > output.txt

--version
++++++++++

Display the version number and exit::

    python solver.py --version

-v, --verbose
++++++++++++++

Run the program in 'verbose' mode, printing messages to console::

    python solver.py -v data/sample_data.json
