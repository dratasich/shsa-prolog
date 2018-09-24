#!/usr/bin/env python3
"""Monitors itoms.

__date__ = 2018-08-29
__author__ = Denise Ratasich

"""

import argparse
import problog


#
# parse arguments
#

parser = argparse.ArgumentParser(description="""Monitors itom logs using a
ProbLog SHSA model.""")
parser.add_argument('model', type=str,
                    help="""SHSA model in Prolog/ProbLog.""")
parser.add_argument('csv', type=str,
                    help="""CSV file of itoms. Header must match the itom names
                    in the model.""")
args = parser.parse_args()


#
# load the model
#

# the models need the path to our custom library
problog.library_paths.append("include")

# load basic model from file
program = ""
with open(args.model, 'r') as f:
    program = f.read()


#
# get the available itoms
#

# split header of csv by ',' to get 'variable:itom'
availability = {}
try:
    with open(args.csv, 'r') as f:
        header = f.readline().strip()
        header = header.split(',')
        for head in header:
            head = head.strip().split(':')
            v = head[0]
            i = head[1]
            if v not in availability.keys():
                availability[v] = []
            availability[v].append(i)
except Exception as e:
    raise SystemExit("Failed to parse CSV-header. Header shall be a list of 'variable:itom'. ")


# append available itoms to program with "itomsOf(variable,[itom1,..])"
program += "\n"
for variable, itoms in availability.items():
    program += "itomsOf({},[{}]).\n".format(variable, ','.join(itoms))

print("Program:\n{}".format(program))


#
# helpers for query evaluation
#

def evaluate(program, queries):
    additional = "\n"
    for query in queries:
        additional += "query({}).\n".format(query)
    model = problog.program.PrologString(program + additional)
    result = problog.get_evaluatable().create_from(model).evaluate()
    return result

def parse_substitution(variable, term):
    """Parses substiution(variable,term)."""
    searchstr = "substitution(" + str(variable) + ","
    start = term.find(searchstr)
    end = term.rfind(")")
    return term[start+len(searchstr):end]


#
# monitor with Prolog model
#

# get all valid substitutions for v
queries = ["substitution(v,S)"]
result = evaluate(program, queries)
# result is a dictionary of {substitution(v,..): 1.0}
print("Queries:\n{}".format(queries))
for r in result.keys():
    # extract substitution
    prolog_substitution = parse_substitution("v", str(r))
    print("  -> " + str(prolog_substitution))

# TODO: execute python functions to get values in common domain
# TODO: agreement on values (Python or Prolog program)
