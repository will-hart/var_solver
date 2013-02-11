var_solver
==========

**Version 0.1**

Use a graph based approach to solve complex inter-related variables intelligently. 


Usage
======

Currently command line only.  Have a look at the `data` directory for some sample json
inputs.  To run, ensure dependencies are installed:

    pip install python-igraph
    pip install sympy

Then from the command line type

    python solver.py data/sample_data.json

A list of help options is available with the `-h` flag.  If you want the output to go
directly to file you can use the `-o` flag and specify a file name, or a better approach
is to simply pipe the results directly to file - e.g. 

    python solver.py data/sample_data.json > output.txt

