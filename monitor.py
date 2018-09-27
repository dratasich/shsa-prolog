#!/usr/bin/env python3
"""Monitors itoms.

__date__ = 2018-08-29
__author__ = Denise Ratasich

"""

import argparse

from model.problog_interface import ProblogInterface


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

pli = ProblogInterface(librarypaths=["./model/"])
pli.load(args.model)


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
program = "\n"
for variable, itoms in availability.items():
    program += "itomsOf({},[{}]).\n".format(variable, ','.join(itoms))

pli.append(program)
print("Program:\n{}".format(pli.program))


#
# monitor with Prolog model
#

# get all valid substitutions for v
result = pli.evaluate("query(substitution(v,S)).")
S = []
for r in result.keys():
    print(r)
    # S.append(pli.parse_substitution(str(r)))
print(S)

# TODO: execute python functions to get values in common domain
# TODO: agreement on values (Python or Prolog program)
