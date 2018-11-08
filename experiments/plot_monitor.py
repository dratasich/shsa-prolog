#!/usr/bin/env python3
"""Plot itoms.

__date__ = 2018-11-08
__author__ = Denise Ratasich

"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# parse arguments
parser = argparse.ArgumentParser(description="""Plots results of `monitor.py`.""")
parser.add_argument("values", type=str,
                    help="""CSV file common domain itoms (outputs [midpoint if
                    interval] of substitutions over time).""")
parser.add_argument("epsilon", type=str,
                    help="""CSV file of epsilons (max deviation of values).""")
parser.add_argument("error", type=str,
                    help="""CSV file of errors (non-intersection of value
                    intervals).""")
args = parser.parse_args()


print("=== loading ====================================================")

values = pd.read_csv(args.values, index_col=0)
print("{:10}: {} rows, columns {}".format("values", len(values), values.columns))

epsilon = pd.read_csv(args.epsilon, index_col=0)
print("{:10}: {} rows, columns {}".format("epsilon", len(epsilon), epsilon.columns))

error = pd.read_csv(args.error, index_col=0)
print("{:10}: {} rows, columns {}".format("error", len(error), error.columns))

assert len(values) == len(epsilon) == len(error)
assert len(values.columns) == len(epsilon.columns) == len(error.columns)

time = values.index


print("=== plotting ===================================================")

colors = list(mcolors.BASE_COLORS.values())
alpha = 0.3
lightcolors = [(r, g, b, alpha) for r, g, b in colors]

# plot error of each substitution
fig, axes = plt.subplots(len(error.columns) + 1, 1, sharex=True)
plt.subplots_adjust(top=0.95, bottom=0.1, hspace=0.2)

for i, column in enumerate(error.columns):
    axes[i].plot(time, error[column], drawstyle='steps')
    axes[i].set_ylabel(column)

for i, column in enumerate(values.columns):
    #ax.errorbar(time, y=values[column], yerr=epsilon[column], capsize=2, linewidth=1)
    lo = values[column] - epsilon[column]
    hi = values[column] + epsilon[column]
    axes[-1].fill_between(time, y1=lo, y2=hi, facecolor=lightcolors[i], step='pre')
    axes[-1].plot(time, values[column], color=colors[i], drawstyle='steps')
    axes[-1].legend(loc='upper left')
    axes[-1].set_ylabel("common domain")
axes[-1].set_ylim(values.values.min() - epsilon.values.max(),
                  values.values.max() + epsilon.values.max())

# plot values in the common domain with epsilon
fig, ax = plt.subplots()

for i, column in enumerate(values.columns):
    #ax.errorbar(time, y=values[column], yerr=epsilon[column], capsize=2, linewidth=1)
    lo = values[column] - epsilon[column]
    hi = values[column] + epsilon[column]
    ax.fill_between(time, y1=lo, y2=hi, facecolor=lightcolors[i], step='pre')
    ax.plot(time, values[column], color=colors[i], drawstyle='steps')
    ax.legend(loc='upper left')
    ax.set_ylabel("common domain")
axes[-1].set_ylim(values.values.min() - epsilon.values.max(),
                  values.values.max() + epsilon.values.max())

plt.show()
