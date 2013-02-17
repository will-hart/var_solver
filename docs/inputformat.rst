Input Format
==============

The input format is JSON encoded, and takes the following format::

    {
        "variables": [
            {"name": "VarName", "relationship": "Optional relationship"},
            ...
        ],
        "start_conditions": {
            "VarName": "VarValue",
            ...
        }
    }

Care should be taken to:

- ensure no trailing comma on the last item in a group
- all variables referenced are declared in the "variables" section

Some examples are shown in the `/data` folder
    