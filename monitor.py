#!/usr/bin/env python3
"""Monitors itoms.

__date__ = 2018-08-29
__author__ = Denise Ratasich

"""

import argparse
import pandas as pd
import numpy as np
from interval import interval
from collections import deque

from model.problog_interface import ProblogInterface
from model.itom import Itom, Itoms


#
# parse arguments
#

parser = argparse.ArgumentParser(description="""Monitors itom logs using a
ProbLog SHSA model.""")
parser.add_argument("--median", "-m", action='store_true',
                    help="""Apply median on error.""")
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

# define epsilon for itoms (static)
epsilon = {
    't_clock': 0,
    'x1': 1,
    'x2': 1,
    'a1': 1,
    'b1': 1,
    'c1': 1,
    'd1': 1,
}


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
# substitution only needs itom names
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
print("query(substitution({},S)).".format(variable))
result = pli.evaluate("query(substitution({},S)).".format(variable))
S = []
for r in result.keys():
    s = pli.parse_substitution(str(r))
    print("\n{}: {}".format(len(S), r))
    print(s)
    S.append(s)

# log
substitution_info = pd.DataFrame({
    'diversity': [s.diversity(set(S) - set([s])) for s in S],
    'num_inputs': [len(s.vin) for s in S],
    'num_functions': [len(s) for s in S],
}, index=np.arange(0, len(S)))
substitution_info.to_csv('substitutions.csv')

# execute python functions to get values in common domain
def bring_to_common_domain(S, itoms):
    """Apply substitutions to itoms.

    Returns values. Values is an ordered dictionary of substitution->itom
    (Itoms with key=substitution).

    """
    output = Itoms()
    for i, s in enumerate(S):
        try:
            result = s.execute(itoms)
            output[s] = result[variable]
        except Exception as e:
            print("Execution failed - value ignored. {}".format(e))
            raise e
    return output

def faulty(outputs):
    # squared error matrix (non-overlap of intervals)
    se = np.zeros((len(values), len(values)))
    for i, v in enumerate(values):
        for j, w in enumerate(values):
            # be sure its an interval
            v = interval(v)
            w = interval(w)
            # error between (1-dimensional) values
            #se[i,j] = (v - w) * (v - w)
            # intersect intervals
            se[i,j] = max(0, max(v[0][0], w[0][0]) - min(v[0][1], w[0][1]))
    return se.sum(1)

# init result arrays
time = data['t_clock']
time = time.rename("t")
size = (len(time), len(S))
columns = np.arange(0, len(S))
s_values = pd.DataFrame(np.zeros(size), index=time, columns=columns)
s_epsilon = pd.DataFrame(np.zeros(size), index=time, columns=columns)
s_error = pd.DataFrame(np.zeros(size), index=time, columns=columns)

print("\n\nMonitor ...")
window = deque(maxlen=5)
for index, row in data.iterrows():
    timestamp = row['t_clock']
    # move values (as intervals) from row to itoms
    for name in itoms.keys():
        v = row[name]
        e = epsilon[name]
        itoms[name].v = interval([v - e, v + e])
        itoms[name].t = timestamp
    # transform
    outputs = bring_to_common_domain(S, itoms)
    # intervals to compare
    values = [output.v for output in outputs.values()]
    # each value is only a single interval (otherwise take the hull first)
    for v in values:
        assert len(v) == 1
    # log
    s_epsilon.at[timestamp, :] = [(v[0][1] - v[0][0])/2 for v in values]
    s_values.at[timestamp, :] = [v.midpoint[0][0] for v in values]
    # compare
    error = faulty(values)
    if args.median:
        window.append(error)
        error = np.median(np.array(window), axis=0)
    if min(error) > 0:
        # faulty values
        idx = list(error).index(max(error))
        print("t = {:2}, faulty (most-likely): {}".format(timestamp, S[idx].vin))
    # log
    s_error.at[timestamp, :] = error

# log all errors, diversity per substitution (by index over time)
s_values.to_csv('values.csv')
s_epsilon.to_csv('epsilon.csv')
s_error.to_csv('error.csv')
print("Done.")
