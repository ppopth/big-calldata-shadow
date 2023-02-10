#!/bin/python
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys
from dateutil import parser

if len(sys.argv) != 4:
    print('usage: histogram.py [start-time] [propagation-time-file] [title]')
    sys.exit(1)

start_time = parser.parse(sys.argv[1]).timestamp()
f = open(sys.argv[2])
nodes = f.readlines()

times = []
for node in nodes:
    times.append(parser.parse(node).timestamp() - start_time)
fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.set_title(f'{sys.argv[3]}')
high=max(times)
if high > 8:
    ax.set_xlabel('time in second, 1s/bin')
else:
    ax.set_xlabel('time in second, 50ms/bin')
ax.set_ylabel('number of nodes')
if high > 8:
    ax.hist(times, np.arange(0, 90, 1))
elif high > 4:
    ax.hist(times, np.arange(0, 8, 0.05))
else:
    ax.hist(times, np.arange(0, 4, 0.05))
fig.savefig(f'histogram.png')
