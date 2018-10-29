#!/usr/bin/env python3
"""Plot itoms.

__date__ = 2018-10-29
__author__ = Denise Ratasich

"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# parse arguments
parser = argparse.ArgumentParser(description="""Plots itoms given a CSV.""")
parser.add_argument("--input", "-i", type=str, nargs='*',
                    help="""Input itoms (give a list of column names, e.g., '-i
                    i1 i2'). These itoms will be displayed in separate
                    plots.""")
parser.add_argument("--common-domain", "-c", type=str, nargs='*',
                    help="""Itoms in the same domain (give a list of column
                    names, e.g., '-c a b'). These itoms will be displayed in
                    the same plot.""")
parser.add_argument("csv", type=str,
                    help="""CSV file containing itoms (values over time). Each
                    column is a separate itom. If -i nor -c is given, all itoms
                    will be printed to separate plots.""")
args = parser.parse_args()


print("=== loading ====================================================")

data = pd.read_csv(args.csv)
print("columns: {}".format(data.columns))
print("{} rows".format(len(data)))

# number of subplots
num_subplots = len(data.columns)

try:
    time = data['t']
    num_subplots = num_subplots - 1
except Exception as e:
    time = np.arange(0,len(data))

# correct subplots given the arguments
if args.input is not None:
    # only given input itoms shall be printed
    # separate plots and in one plot
    num_subplots = len(args.input) + 1
    if args.common_domain is not None:
        # additionally a plot with the itoms in the common domain
        num_subplots = num_subplots + 1
else:
    if args.common_domain is not None:
        # print only one plot of common domain itoms
        num_subplots = 1


print("=== plotting ===================================================")

fig, axes = plt.subplots(num_subplots, 1)
plt.subplots_adjust(top=0.95, bottom=0.1, hspace=0.5)

# general axis settings
plt.xlabel("time")
for ax in axes:
    ax.set_xlim(min(time), max(time))
    ax.set_ylim(-3, 3)

# plot all
if args.input is None and args.common_domain is None:
    for i, column in enumerate(data.columns):
        axes[i].plot(time, data[column])
        axes[i].set_ylabel(column)

# plot inputs
if args.input is not None:
    print("plot input itoms")
    all_i = len(args.input)
    for i, column in enumerate(args.input):
        axes[i].plot(time, data[column])
        axes[i].set_ylabel(column)
        axes[all_i].plot(time, data[column])
    axes[all_i].set_ylabel("input itoms")

# plot common domain
if args.input is not None:
    print("plot common domain")
    for column in args.common_domain:
        axes[-1].plot(time, data[column])
    axes[-1].legend(loc='upper left')
    axes[-1].set_ylabel("common domain")

plt.show()
