#!/bin/python

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
from dateutil import parser

if len(sys.argv) < 2:
    print('usage: mainnet.py [log-file]')
    sys.exit(1)

genesis = 1606824023
delays = []
sizes = []

# Block size distribution
fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.set_title(f'Block size distribution in mainnet')
ax.set_xlabel('block size (KB)')
ax.set_ylabel('probability density function (pdf)')
ax.set_xticks(np.arange(0, 700, 100));
ax.set_xticks(np.arange(0, 700, 20), minor=True);

fname = sys.argv[1]
f = open(fname)
for line in f.readlines():
    m = re.search(r'^.*lighthouse.*: (.*) INFO New block received.*size: (\d+), slot: (\d+)', line)
    if m == None:
        continue
    time = parser.parse(m.group(1) + " UTC")
    size = int(m.group(2))
    slot = int(m.group(3))
    slot_time = slot * 12 + genesis;
    delay = time.timestamp() - slot_time
    sizes.append(size/1024)
    delays.append(delay)
    print(slot, size, delay)

ax.hist(sizes, np.arange(0, 700, 10), density=True, histtype='step')
ax.axvline(np.median(sizes), color='k', label="median", linestyle='dashed', linewidth=1)
ax.legend()
fig.savefig(f'block-size.png')

# Block size of 300-400KB
fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.set_title(f'Propagation time of 300KB-400KB blocks in mainnet')
ax.set_xlabel('time in second')
ax.set_ylabel('probability density function (pdf)')
ax.set_xticks(np.arange(0, 10, 1.0));
ax.set_xticks(np.arange(0, 10, 0.5), minor=True);
filtered_delays = []
filtered_sizes = []

for delay, size in zip(delays, sizes):
    if size >= 300 and size < 400:
        filtered_delays.append(delay)
        filtered_sizes.append(size)

ax.hist(filtered_delays, np.arange(0, 10, 0.1), density=True, histtype='step')
ax.axvline(np.median(filtered_delays), color='k', label="median", linestyle='dashed', linewidth=1)
ax.legend()
fig.savefig(f'hist-300-400KB.png')

# Block size of 400-500KB
fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.set_title(f'Propagation time of 400KB-500KB blocks in mainnet')
ax.set_xlabel('time in second')
ax.set_ylabel('probability density function (pdf)')
ax.set_xticks(np.arange(0, 10, 1.0));
ax.set_xticks(np.arange(0, 10, 0.5), minor=True);
filtered_delays = []
filtered_sizes = []

for delay, size in zip(delays, sizes):
    if size >= 400 and size < 500:
        filtered_delays.append(delay)
        filtered_sizes.append(size)

ax.hist(filtered_delays, np.arange(0, 10, 0.1), density=True, histtype='step')
ax.axvline(np.median(filtered_delays), color='k', label="median", linestyle='dashed', linewidth=1)
ax.axvline(np.percentile(filtered_delays, 90), color='r', label="percentile 90", linewidth=1)
ax.legend()
fig.savefig(f'hist-400-500KB.png')

# All block sizes
fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.set_title(f'Propagation time of the blocks in mainnet')
ax.set_xlabel('time in second')
ax.set_ylabel('probability density function (pdf)')
ax.set_xticks(np.arange(0, 10, 1.0));
ax.set_xticks(np.arange(0, 10, 0.5), minor=True);
filtered_delays = []
filtered_sizes = []

for delay, size in zip(delays, sizes):
    filtered_delays.append(delay)
    filtered_sizes.append(size)

ax.hist(filtered_delays, np.arange(0, 10, 0.1), density=True, histtype='step')
ax.axvline(np.median(filtered_delays), color='k', label="median", linestyle='dashed', linewidth=1)
percentile = 99.3
ax.axvline(np.percentile(filtered_delays, percentile), color='r', label="percentile " + str(percentile), linewidth=1)
ax.legend()
fig.savefig(f'hist-pg-time.png')
