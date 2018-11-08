#!/usr/bin/env python3
"""Plot itoms.

__date__ = 2018-11-08
__author__ = Denise Ratasich

"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt

# parse arguments
parser = argparse.ArgumentParser(description="""Plots substitutions info of `monitor.py`.""")
parser.add_argument("data", type=str,
                    help="""CSV file containing information of substitutions.""")
args = parser.parse_args()


print("=== loading ====================================================")

data = pd.read_csv(args.data, index_col=0)
print("{} rows, columns {}".format(len(data), data.columns))


print("=== plotting ===================================================")

# plot values in the common domain with epsilon
fig, ax = plt.subplots()

ax.bar(data.index, data['diversity']/(len(data.index)-1), label='diversity/{}'.format((len(data.index)-1)))
bot = data['diversity']/(len(data.index)-1)
ax.bar(data.index, 1/data['num_inputs'], bottom=bot, label="1/num_inputs")
bot = data['diversity']/(len(data.index)-1) + 1/data['num_inputs']
ax.bar(data.index, 1/data['num_functions'], bottom=bot, label="1/num_functions")
ax.legend(loc='upper right')
ax.set_xlabel("substitution")
ax.set_ylabel("rank")

plt.show()
