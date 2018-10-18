#!/usr/bin/env python3
"""Monitors itoms.

__date__ = 2018-08-29
__author__ = Denise Ratasich

"""

import argparse
import pandas as pd

from model.problog_interface import ProblogInterface
from model.itom import Itom, Itoms


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

try:
    data = pd.read_csv(args.csv)
except Exception as e:
    raise SystemExit("Failed to parse csv. {}".format(e))

# get variable/itoms available from column name (header) 'variable:itom'
itoms = Itoms()
try:
    for head in data.columns.values:
        head = head.strip().split(':')
        v = head[0]
        i = head[1]
        # empty value and timestamp for this itom describing the header only
        itom = Itom(i, None, variable=v, timestamp=None)
        itoms[itom.name] = itom
except Exception as e:
    raise SystemExit("Failed to parse column name 'variable:itom'. {}".format(e))

# problog knows the mapping now, so we can change the column names to itoms only
# substiution only needs itom names
data.columns = itoms.keys()

# append available itoms to program with "itomsOf(variable,[itom1,..])"
program = "\n"
for variable, il in itoms.availability.items():
    names = [itom.name for itom in il]
    program += "itomsOf({},[{}]).\n".format(variable, ','.join(names))

pli.append(program)
print("Program:\n{}".format(pli.program))


#
# monitor with Prolog model
#

# variable to monitor
variable = 'x'

# get all valid substitutions for v
result = pli.evaluate("query(substitution({},S)).".format(variable))
S = []
for r in result.keys():
    s = pli.parse_substitution(str(r))
    S.append(s)

# execute python functions to get values in common domain
def bring_to_common_domain(S, itoms):
    values = {}
    for i, s in enumerate(S):
        print("\nSubstitution {}".format(i))
        print(s)
        try:
            result = s.execute(itoms)
            values[s] = result[variable]
        except Exception as e:
            print("Execution failed - value ignored. {}".format(e))
            raise e
    return values

# TODO: agreement on values (Python or Prolog program)
for index, row in data.iterrows():
    timestamp = row['t_clock']
    # set values in the row to itoms
    il = list(itoms.values())
    assert len(il) == len(row)
    for i, value in enumerate(row):
        il[i].v = value
        il[i].t = timestamp
    values = bring_to_common_domain(S, il)
    print([itom.v for itom in values.values()])
    raise SystemExit("Stop.")
